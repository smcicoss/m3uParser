def main(request):
    from flask import send_file, abort
    import requests
    from urllib.parse import urlparse

    class M3uDownload(object):
        def __init__(self, user_id, user_pwd):
            self.url = f'http://tvservice.pro:80/get.php?username={user_id}&password={user_pwd}&type=m3u&output=ts'

        def get(self):
            r = requests.get(self.url)
            if r.status_code == 200:
                return r.text
            else:
                return None

    class M3uParser(object):
        _LIVE = 'live'

        def __init__(self, m3u):
            self.lines = m3u.splitlines()
            self.epg = Epg()

        def parse(self):
            for num, line in enumerate(self.lines):
                if line.startswith('#EXTINF:'):
                    group = M3uParser.extract_group(self.lines[num + 1])
                    if self.is_fr(line):
                        if group == M3uParser._LIVE and self.has_epg(line):
                            self.lines[num] = self.add_epg(line.replace(',', f' group-title="{group} FR",', 1))
                        elif group == M3uParser._LIVE:
                            self.lines[num] = line.replace(',', f' group-title="{group} FR without EPG",', 1)
                        else:
                            self.lines[num] = line.replace(',', f' group-title="{group} FR",', 1)
                    else:
                        self.lines[num] = line.replace(',', f' group-title="{group}",', 1)
            return '\n'.join(self.lines)

        @staticmethod
        def extract_group(url):
            parts = urlparse(url).path.split('/')
            if len(parts) == 5:
                return parts[1]
            elif len(parts) == 4:
                return M3uParser._LIVE
            else:
                return 'empty'

        def is_fr(self, line):
            return line.startswith('#EXTINF:-1,FR') or line.startswith('#EXTINF:-1,|FR|')

        def has_epg(self, line):
            channel = line.split(',')[1]
            return channel in self.epg.channels()

        def add_epg(self, line):
            ext_inf = line.split(',')
            tvg = self.epg.find(ext_inf[1])
            tvg_id = tvg['channel_id']
            tvg_logo = tvg['channel_logo']
            tvg_name = tvg['channel_name']
            ext_inf[0] += f' tvg-id="{tvg_id}" tvg-logo="{tvg_logo}"'
            ext_inf[1] = tvg_name
            return ','.join(ext_inf)

    class Epg(object):
        def __init__(self):
            self.epg = dict()
            self.epg['FR - TF1 FHD'] = {'channel_name': 'TF1', 'channel_id': 'TF1.fr', 'channel_logo': 'http://i.imgur.com/SPe8thD.png'}
            self.epg['FR - FRANCE 2 FHD'] = {'channel_name': 'France 2', 'channel_id': 'France2.fr', 'channel_logo': 'http://i.imgur.com/afmgqyh.png'}
            self.epg['FR - FRANCE 3 FHD'] = {'channel_name': 'France 3', 'channel_id': 'France3.fr', 'channel_logo': 'http://i.imgur.com/F8oz4Dn.png'}
            self.epg['FR - FRANCE 4 FHD'] = {'channel_name': 'France 4', 'channel_id': 'France4.fr', 'channel_logo': 'http://i.imgur.com/4kXbmF4.png'}
            self.epg['FR - FRANCE 5 FHD'] = {'channel_name': 'France 5', 'channel_id': 'France5', 'channel_logo': 'http://i.imgur.com/sAecfZH.png'}
            self.epg['FR - FRANCE O FHD'] = {'channel_name': 'France Ô', 'channel_id': 'FranceO.fr', 'channel_logo': 'http://i.imgur.com/Snb23KJ.png'}
            self.epg['FR - M6 FHD'] = {'channel_name': 'M6', 'channel_id': 'M6.fr', 'channel_logo': 'http://i.imgur.com/LNeK7Ut.jpg'}
            self.epg['FR - TMC FHD'] = {'channel_name': 'TMC', 'channel_id': 'TMC.fr', 'channel_logo': 'http://i.imgur.com/1Nq8rTR.jpg'}
            self.epg['FR - TV BREIZH FHD'] = {'channel_name': 'TV Breizh', 'channel_id': 'TVBreizh', 'channel_logo': 'http://i.imgur.com/DTVhBEW.png'}
            self.epg['FR - 6TER FHD'] = {'channel_name': '6ter', 'channel_id': '6ter.fr', 'channel_logo': 'http://i.imgur.com/0KLslG3.png'}
            self.epg['FR - ARTE FHD'] = {'channel_name': 'Arte', 'channel_id': 'Arte.fr', 'channel_logo': 'http://i.imgur.com/4bCacaZ.png'}
            self.epg['FR - CANAL  FHD'] = {'channel_name': 'Canal +', 'channel_id': 'CANALplus.fr', 'channel_logo': 'http://i.imgur.com/DXiNFLz.png'}
            self.epg['FR - CANAL  DECALE FHD'] = {'channel_name': 'Canal + Décalé', 'channel_id': 'CANALplusDECALE.fr', 'channel_logo': 'http://i.imgur.com/wKRT7Lo.png'}
            self.epg['FR - CANAL  FAMILY FHD'] = {'channel_name': 'Canal + Family', 'channel_id': 'CANALplusFamily.fr', 'channel_logo': 'http://i.imgur.com/uxeoZaw.png'}
            self.epg['FR - CANAL  CINEMA FHD'] = {'channel_name': 'Canal + Cinéma', 'channel_id': 'CANALplusCINEMA.fr', 'channel_logo': 'http://i.imgur.com/Jxrqw54.png'}
            self.epg['FR - OCS MAX FHD'] = {'channel_name': 'OCS Max', 'channel_id': 'OCSMax', 'channel_logo': 'http://i.imgur.com/qGbatCm.png'}
            self.epg['FR - OCS GEANTS FHD'] = {'channel_name': 'OCS Géants', 'channel_id': 'OCSGeants', 'channel_logo': 'http://i.imgur.com/tTEiZ9a.jpg'}
            self.epg['FR - OCS CITY FHD'] = {'channel_name': 'OCS City', 'channel_id': 'OCSCity', 'channel_logo': 'http://upload.wikimedia.org/wikipedia/fr/thumb/6/6d/OCS_City.svg/128px-OCS_City.svg.png'}
            self.epg['FR - OCS CHOC FHD'] = {'channel_name': 'OCS Choc', 'channel_id': 'OCSChoc', 'channel_logo': 'http://i.imgur.com/7o2SoPK.png'}
            self.epg['FR - CINE  PREMIER FHD'] = {'channel_name': 'Ciné+ Premier', 'channel_id': 'CinecinemaPremier.fr', 'channel_logo': 'http://i.imgur.com/JD7AiiU.png'}
            self.epg['FR - CINE  FRISSON FHD'] = {'channel_name': 'Ciné+ Frisson', 'channel_id': 'CinecinemaFrisson.fr', 'channel_logo': 'http://i.imgur.com/2aHAClZ.png'}
            self.epg['FR - CINE  FAMIZ FHD'] = {'channel_name': 'Ciné+ Famiz', 'channel_id': 'CinecinemaFamiz.fr', 'channel_logo': 'http://i.imgur.com/GPL2t1N.png'}
            self.epg['FR - CINE  EMOTION FHD'] = {'channel_name': 'Ciné+ Emotion', 'channel_id': 'CinecinemaEmotion.fr', 'channel_logo': 'http://i.imgur.com/NjTh0jJ.png'}
            self.epg['FR - ACTION FHD'] = {'channel_name': 'Action', 'channel_id': 'Action', 'channel_logo': 'http://i.imgur.com/zXkxYG0.png'}
            self.epg['FR - CINE  CLUB FHD'] = {'channel_name': 'Ciné+ Club', 'channel_id': 'CinecinemaClub.fr', 'channel_logo': 'http://i.imgur.com/UkRWhEQ.png'}
            self.epg['FR - CINE POLAR FHD'] = {'channel_name': 'Polar +', 'channel_id': 'PolarPlus', 'channel_logo': 'http://i.imgur.com/IUAo8Qh.jpg'}
            self.epg['FR - CINE  CLASSIC FHD'] = {'channel_name': 'Ciné+ Classic', 'channel_id': 'CinecinemaClassic.fr', 'channel_logo': 'http://i.imgur.com/ZCoVZ1K.png'}
            self.epg['FR - CINE FX FHD'] = {'channel_name': 'Ciné FX', 'channel_id': 'CineFX', 'channel_logo': 'http://i.imgur.com/uViZQ9J.png'}
            self.epg['FR - PARAMOUNT CHANNEL FHD'] = {'channel_name': 'Paramount Channel', 'channel_id': 'ParamountChannel.fr', 'channel_logo': 'http://i.imgur.com/okyHY86.png'}
            self.epg['FR - CANAL  SERIES FHD'] = {'channel_name': 'Canal + Séries', 'channel_id': 'CanalplusSeries.fr', 'channel_logo': 'http://i.imgur.com/AQGe8AX.png'}
            self.epg['FR - CANAL  SPORT FHD'] = {'channel_name': 'Canal + Sport', 'channel_id': 'CANALplusSPORT.fr', 'channel_logo': 'http://i.imgur.com/KucgW8D.png'}
            self.epg['FR - BEINSPORT1 FHD'] = {'channel_name': 'beIN Sports 1', 'channel_id': 'beINSPORTS1', 'channel_logo': 'http://i.imgur.com/W3OfHnq.png'}
            self.epg['FR - BEINSPORT2 FHD'] = {'channel_name': 'beIN Sports 2', 'channel_id': 'beINSPORTS2', 'channel_logo': 'http://i.imgur.com/D7UzWf4.png'}
            self.epg['FR - BEINSPORT3 FHD'] = {'channel_name': 'beIN Sports 3', 'channel_id': 'beINSPORTS3', 'channel_logo': 'http://i.imgur.com/tB17ocB.png'}
            self.epg['FR - BFM TV FHD'] = {'channel_name': 'BFM TV', 'channel_id': 'BFMTV.fr', 'channel_logo': 'http://i.imgur.com/Ry0M4Y0.png'}
            self.epg['FR - INFOSPORT FHD'] = {'channel_name': 'InfoSport+', 'channel_id': 'Infosportplus', 'channel_logo': 'http://i.imgur.com/HjC5C8e.png'}
            self.epg['FR - L\'EQUIPE21 FHD'] = {'channel_name': 'L\'Equipe TV', 'channel_id': 'EquipeTV.fr', 'channel_logo': 'http://i.imgur.com/Z1IELMD.jpg'}
            self.epg['FR - MOTORSPORT TV FHD'] = {'channel_name': 'Motors TV', 'channel_id': 'MotorsTVFrance', 'channel_logo': 'http://i.imgur.com/PVKmj7U.png'}
            self.epg['FR - EUROSPORT1 FHD'] = {'channel_name': 'Eurosport', 'channel_id': 'EurosportFrance', 'channel_logo': 'http://i.imgur.com/z97dwpW.png'}
            self.epg['FR - EUROSPORT2 FHD'] = {'channel_name': 'Eurosport 2', 'channel_id': 'Eurosport2France', 'channel_logo': 'http://i.imgur.com/BwKJBmp.png'}
            self.epg['FR - EXTREME SPORTS FHD'] = {'channel_name': 'Extreme Sports', 'channel_id': 'ExtremeSports1', 'channel_logo': 'http://i.imgur.com/zD8LmnW.png'}
            self.epg['FR - EQUIDIA LIVE FHD'] = {'channel_name': 'Equidia', 'channel_id': 'EquidiaLive.fr', 'channel_logo': 'http://i.imgur.com/Aut1wmM.jpg'}
            self.epg['FR - SFR SPORT1 FHD'] = {'channel_name': 'SFR Sport 1', 'channel_id': 'SFRSport1.fr', 'channel_logo': 'https://upload.wikimedia.org/wikipedia/fr/thumb/e/e4/Logo_SFR_Sport_1_2016.svg/320px-Logo_SFR_Sport_1_2016.svg.png'}
            self.epg['FR - SFR SPORT2 FHD'] = {'channel_name': 'SFR Sport 2', 'channel_id': 'SFRSport2.fr', 'channel_logo': 'https://upload.wikimedia.org/wikipedia/fr/thumb/e/e9/Logo_SFR_Sport_2_2016.svg/320px-Logo_SFR_Sport_2_2016.svg.png'}
            self.epg['FR - SFR SPORT3 FHD'] = {'channel_name': 'SFR Sport 3', 'channel_id': 'SFRSport3.fr', 'channel_logo': 'https://upload.wikimedia.org/wikipedia/fr/thumb/8/80/Logo_SFR_Sport_3_2016.svg/320px-Logo_SFR_Sport_3_2016.svg.png'}
            self.epg['FR - SFR SPORT5 FHD'] = {'channel_name': 'SFR Sport 5', 'channel_id': 'SFRSport5.fr', 'channel_logo': 'https://upload.wikimedia.org/wikipedia/fr/thumb/1/19/Logo_SFR_Sport_5_2016.svg/320px-Logo_SFR_Sport_5_2016.svg.png'}
            self.epg['FR - GOLF  FHD'] = {'channel_name': 'Golf+', 'channel_id': 'Golfplus', 'channel_logo': 'http://i.imgur.com/SKnHBDP.png'}
            self.epg['FR - GOLF CHANNEL FHD'] = {'channel_name': 'Golf Channel', 'channel_id': 'GolfChannel', 'channel_logo': 'http://i.imgur.com/QWmVLLD.png'}
            self.epg['FR - 13EME RUE FHD'] = {'channel_name': '13ème Rue', 'channel_id': '13eRue', 'channel_logo': 'http://i.imgur.com/1GdYZEh.png'}
            self.epg['FR - COMEDIE  FHD'] = {'channel_name': 'Comédie +', 'channel_id': 'Comedie.fr', 'channel_logo': 'http://i.imgur.com/R5dKwxW.png'}
            self.epg['FR - E! ENTERTAINMENT FHD'] = {'channel_name': 'Entertainment Television', 'channel_id': 'E!F', 'channel_logo': 'http://i.imgur.com/jUMdWkW.png'}
            self.epg['FR - BET FHD'] = {'channel_name': 'BET', 'channel_id': 'BET', 'channel_logo': 'http://i.imgur.com/VGkv6fN.png'}
            self.epg['FR - CHERIE 25 FHD'] = {'channel_name': 'Chérie 25', 'channel_id': 'Cherie25.fr', 'channel_logo': 'http://i.imgur.com/XBbSuHv.png'}
            self.epg['FR - CSTAR FHD'] = {'channel_name': 'CStar', 'channel_id': 'CStar.fr', 'channel_logo': 'http://i.imgur.com/sSNnVvX.png'}
            self.epg['FR - RTL9 FHD'] = {'channel_name': 'RTL9', 'channel_id': 'RTL9.fr', 'channel_logo': 'http://i.imgur.com/R83Gja0.png'}
            self.epg['FR - RMC STORY FHD'] = {'channel_name': 'Numéro 23', 'channel_id': 'Numero23.fr', 'channel_logo': 'http://i.imgur.com/yPbXCXK.jpg'}
            self.epg['FR - W9 FHD'] = {'channel_name': 'W9', 'channel_id': 'W9.fr', 'channel_logo': 'http://i.imgur.com/EqNY1J7.png'}
            self.epg['FR - AB3 FHD'] = {'channel_name': 'AB3', 'channel_id': 'AB3', 'channel_logo': 'http://i.imgur.com/zYlOI2F.png'}
            self.epg['FR - CANAL8 FHD'] = {'channel_name': 'C8', 'channel_id': 'C8.fr', 'channel_logo': 'http://i.imgur.com/J30PQOP.png'}
            self.epg['FR - RTS DEUX FHD'] = {'channel_name': 'RTS Deux', 'channel_id': 'RTSDeux', 'channel_logo': 'http://i.imgur.com/bVgMR4f.png'}
            self.epg['FR - RTS UN FHD'] = {'channel_name': 'RTS Un', 'channel_id': 'RTSUn', 'channel_logo': 'http://i.imgur.com/dVkikAF.png'}
            self.epg['FR - ONE TV FHD'] = {'channel_name': 'One TV', 'channel_id': 'One TV', 'channel_logo': 'https://upload.wikimedia.org/wikipedia/fr/d/d8/ONEtv.png'}
            self.epg['FR - TCM CINEMA FHD'] = {'channel_name': 'TCM Cinéma', 'channel_id': 'TCMcinema', 'channel_logo': 'http://i.imgur.com/Qk4524d.png'}
            self.epg['FR - CRIME DISTRICT FHD'] = {'channel_name': 'Crime District', 'channel_id': 'CrimeDistrict', 'channel_logo': 'http://i.imgur.com/oZNVuaY.png'}
            self.epg['FR - SYFY FHD'] = {'channel_name': 'SyFy', 'channel_id': 'SyFyF', 'channel_logo': 'http://i.imgur.com/RSxEphS.jpg'}
            self.epg['FR -ELLE GIRL FHD'] = {'channel_name': 'Elle Girl', 'channel_id': 'ElleGirl', 'channel_logo': 'http://i.imgur.com/FayKzhQ.png'}
            self.epg['FR - AB1 FHD'] = {'channel_name': 'AB1', 'channel_id': 'AB1.fr', 'channel_logo': 'http://i.imgur.com/m5C85Z8t.jpg'}
            self.epg['FR - NT1 FHD'] = {'channel_name': 'TFX', 'channel_id': 'NT1.fr', 'channel_logo': 'https://upload.wikimedia.org/wikipedia/fr/thumb/8/83/TFX_logo_2018.svg/320px-TFX_logo_2018.svg.png'}
            self.epg['FR - RFM TV FHD'] = {'channel_name': 'RFM TV', 'channel_id': 'RFMTV', 'channel_logo': 'http://i.imgur.com/fcj1TOB.png'}
            self.epg['FR - DISNEY CHANNEL FHD'] = {'channel_name': 'Disney Channel', 'channel_id': 'DisneyChannel', 'channel_logo': 'http://i.imgur.com/5BqiTRp.png'}
            self.epg['FR - DISNEY XD FHD'] = {'channel_name': 'Disney XD', 'channel_id': 'DisneyXD', 'channel_logo': 'http://i.imgur.com/Jwq94HS.png'}
            self.epg['FR - NICKELODEON FHD'] = {'channel_name': 'Nickelodeon', 'channel_id': 'NickelodeonFr', 'channel_logo': 'http://i.imgur.com/VCrQm3X.png'}
            self.epg['FR - PIWI FHD'] = {'channel_name': 'Piwi+', 'channel_id': 'PIWI.fr', 'channel_logo': 'http://i.imgur.com/eMeGbZgt.jpg'}
            self.epg['FR - BOOMERANG FHD'] = {'channel_name': 'Boomerang', 'channel_id': 'BoomerangF', 'channel_logo': 'http://i.imgur.com/yCuIJ2p.png'}
            self.epg['FR - DISNEY JUNIOR FHD'] = {'channel_name': 'Disney Junior', 'channel_id': 'DisneyJunior', 'channel_logo': 'http://i.imgur.com/AfRnyPat.jpg'}
            self.epg['FR - CARTOON NETWORK FHD'] = {'channel_name': 'Cartoon Network', 'channel_id': 'CartoonNetwork', 'channel_logo': 'http://i.imgur.com/FDfrEnR.png'}
            self.epg['FR - CANAL J FHD'] = {'channel_name': 'Canal J', 'channel_id': 'CanalJ', 'channel_logo': 'http://i.imgur.com/B6CJSaS.png'}
            self.epg['FR - TIJI FHD'] = {'channel_name': 'Tiji', 'channel_id': 'Tiji', 'channel_logo': 'http://i.imgur.com/R3aY39E.jpg'}
            self.epg['FR - BOING FHD'] = {'channel_name': 'Boing', 'channel_id': 'Boing', 'channel_logo': 'http://i.imgur.com/LQuPvPg.png'}
            self.epg['FR - TELETOON  FHD'] = {'channel_name': 'Télétoon +', 'channel_id': 'TeleTOON.fr', 'channel_logo': 'http://i.imgur.com/2Q5UJV1.png'}
            self.epg['FR - GAME ONE FHD'] = {'channel_name': 'Game One', 'channel_id': 'GameOne.fr', 'channel_logo': 'http://i.imgur.com/xiTNtjA.png'}
            self.epg['FR - GULLI FHD'] = {'channel_name': 'Gulli', 'channel_id': 'Gulli.fr', 'channel_logo': 'http://i.imgur.com/uzplnrs.jpg'}
            self.epg['FR - MANGA FHD'] = {'channel_name': 'Mangas', 'channel_id': 'Mangas', 'channel_logo': 'http://i.imgur.com/3Af8zGF.png'}
            self.epg['FR - DISNEY CINEMA FHD'] = {'channel_name': 'Disney Cinéma', 'channel_id': 'DisnCineHD', 'channel_logo': 'http://i.imgur.com/d9i60jG.png'}
            self.epg['FR - PLANETE  FHD'] = {'channel_name': 'Planète +', 'channel_id': 'PLANETE.fr', 'channel_logo': 'http://i.imgur.com/falwfBJ.png'}
            self.epg['FR - PLANETE AE FHD'] = {'channel_name': 'Planète + Action & Expérience', 'channel_id': 'PLANETEnoLIMIT.fr', 'channel_logo': 'http://i.imgur.com/dhDWTjB.jpg'}
            self.epg['FR - PLANETE CI FHD'] = {'channel_name': 'Planète + Crime Investigation', 'channel_id': 'PLANETEJustice.fr', 'channel_logo': 'http://i.imgur.com/l09wopF.jpg'}
            self.epg['FR - DISCOVERY FHD'] = {'channel_name': 'Discovery Channel', 'channel_id': 'DiscoveryChannelFrance', 'channel_logo': 'http://i.imgur.com/3xSsJs2.jpg'}
            self.epg['FR - DISCOVERY SCIENCE FHD'] = {'channel_name': 'Discovery Science', 'channel_id': 'DiscoveryScience', 'channel_logo': 'http://i.imgur.com/wUm3hYJ.png'}
            self.epg['FR - NGC FHD'] = {'channel_name': 'National Géographic', 'channel_id': 'NationalGeographicChannelFrance', 'channel_logo': 'http://i.imgur.com/xbVAVt6.png'}
            self.epg['FR - NGC WILD FHD'] = {'channel_name': 'Nat Geo Wild', 'channel_id': 'NatGeoWildFrance', 'channel_logo': 'http://i.imgur.com/Vhqpefo.jpg'}
            self.epg['FR - ANIMAUX FHD'] = {'channel_name': 'Animaux', 'channel_id': 'Animaux', 'channel_logo': 'http://i.imgur.com/GS1KA7E.png'}
            self.epg['FR - USHUAIA TV FHD'] = {'channel_name': 'Ushuaïa TV', 'channel_id': 'Ushuaia', 'channel_logo': 'http://i.imgur.com/C0fjS02.png'}
            self.epg['FR - RMC DECOUVERTE FHD'] = {'channel_name': 'RMC Découverte', 'channel_id': 'RMCdecouverte.fr', 'channel_logo': 'http://i.imgur.com/trOS4YC.jpg'}
            self.epg['FR - VOYAGE FHD'] = {'channel_name': 'Voyage', 'channel_id': 'Voyage', 'channel_logo': 'http://i.imgur.com/dWk2Eh8.png'}
            self.epg['FR - TREK FHD'] = {'channel_name': 'Trek TV', 'channel_id': 'TREK', 'channel_logo': 'http://i.imgur.com/HNNgLhZ.jpg'}
            self.epg['FR - HISTOIRE FHD'] = {'channel_name': 'Histoire', 'channel_id': 'Histoire', 'channel_logo': 'http://i.imgur.com/gwTrWaI.png'}
            self.epg['FR - SCIENCES & VIE FHD'] = {'channel_name': 'Science & Vie TV', 'channel_id': 'ScienceetVieTV', 'channel_logo': 'http://i.imgur.com/rPyPM6A.jpg'}
            self.epg['FR - SEASON FHD'] = {'channel_name': 'Seasons', 'channel_id': 'Seasons.fr', 'channel_logo': 'http://i.imgur.com/3wZw8jg.jpg'}
            self.epg['FR - CANAL NEWS FHD'] = {'channel_name': 'CNews', 'channel_id': 'CNews.fr', 'channel_logo': 'http://i.imgur.com/jPxb96q.png'}
            self.epg['FR - BFM BUSINESS FHD'] = {'channel_name': 'BFM Business', 'channel_id': 'BFMBusiness.fr', 'channel_logo': 'http://i.imgur.com/ItnrrLN.jpg'}
            self.epg['FR - LCI FHD'] = {'channel_name': 'LCI', 'channel_id': 'LCI', 'channel_logo': 'http://i.imgur.com/6c3XoyY.jpg'}
            self.epg['FR - FRANCE INFO FHD'] = {'channel_name': 'franceinfo:', 'channel_id': 'franceinfo', 'channel_logo': 'http://i.imgur.com/oiT5v91.jpg'}
            self.epg['FR - I24 NEWS FHD'] = {'channel_name': 'i24 News', 'channel_id': 'i24News', 'channel_logo': 'http://i.imgur.com/FVXhsJ1.png'}
            self.epg['FR - TRACE URBAN FHD'] = {'channel_name': 'Trace Urban', 'channel_id': 'TraceUrban', 'channel_logo': 'http://i.imgur.com/pma4sRi.jpg'}
            self.epg['FR - MTV FRANCE FHD'] = {'channel_name': 'MTV', 'channel_id': 'MTVF', 'channel_logo': 'http://i.imgur.com/Z16ZNwZ.jpg'}
            self.epg['FR - MTV HITS FHD'] = {'channel_name': 'MTV Hits', 'channel_id': 'MTVHits', 'channel_logo': 'http://i.imgur.com/vHm1yro.png'}
            self.epg['FR - MCM TOP FHD'] = {'channel_name': 'MCM Top', 'channel_id': 'MCMTop', 'channel_logo': 'http://i.imgur.com/Chi1JdV.png'}
            self.epg['FR - MCM FHD'] = {'channel_name': 'MCM', 'channel_id': 'MCM.fr', 'channel_logo': 'http://i.imgur.com/34RVngzt.jpg'}
            self.epg['FR - MEZZO FHD'] = {'channel_name': 'Mezzo', 'channel_id': 'Mezzo', 'channel_logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Mezzo_Logo.svg/langfr-800px-Mezzo_Logo.svg.png'}
            self.epg['FR - MEZZO LIVE FHD'] = {'channel_name': 'MezzoLive', 'channel_id': 'MezzoLive', 'channel_logo': 'https://upload.wikimedia.org/wikipedia/fr/f/f0/Mezzo_Live_HD.png'}
            # HD
            self.epg['FR - PARIS PREMIERE HD'] = {'channel_name': 'Paris Première', 'channel_id': 'ParisPremiere.fr', 'channel_logo': 'http://i.imgur.com/aNCGIoP.jpg'}
            self.epg['FR - CANAL SAVOIR HD'] = {'channel_name': 'Canal Savoir', 'channel_id': 'CanalSavoir', 'channel_logo': 'http://i.imgur.com/vRXllgy.png'}
            self.epg['FR - R SPORT NEWS'] = {'channel_name': 'RMC Sport News', 'channel_id': 'RMC Sport News', 'channel_logo': 'http://i.imgur.com/599r2Dv.png'}
            self.epg['FR - R SPORT 1 HD'] = {'channel_name': 'RMC Sport 1', 'channel_id': 'SFRSport1.fr', 'channel_logo': 'http://i.imgur.com/599r2Dv.png'}
            self.epg['FR - R SPORT 2 HD'] = {'channel_name': 'RMC Sport 2', 'channel_id': 'SFRSport2.fr', 'channel_logo': 'http://i.imgur.com/599r2Dv.png'}
            self.epg['FR - R SPORT 3 HD'] = {'channel_name': 'RMC Sport 3', 'channel_id': 'SFRSport3.fr', 'channel_logo': 'http://i.imgur.com/599r2Dv.png'}
            self.epg['FR - R SPORT 4 HD'] = {'channel_name': 'RMC Sport 4', 'channel_id': 'SFRSport5.fr', 'channel_logo': 'http://i.imgur.com/599r2Dv.png'}
            self.epg['FR - R SPORT 5 HD'] = {'channel_name': 'RMC Sport 5', 'channel_id': 'RMCSportLive5', 'channel_logo': 'http://i.imgur.com/599r2Dv.png'}
            self.epg['FR - R SPORT 6 HD'] = {'channel_name': 'RMC Sport 6', 'channel_id': 'RMCSportLive6', 'channel_logo': 'http://i.imgur.com/599r2Dv.png'}
            self.epg['FR - R SPORT 7 HD'] = {'channel_name': 'RMC Sport 7', 'channel_id': 'RMCSportLive7', 'channel_logo': 'http://i.imgur.com/599r2Dv.png'}
            self.epg['FR - BEIN SPORT MAX 4 HD'] = {'channel_name': 'beIN Sports MAX 4', 'channel_id': 'beINSPORTS4', 'channel_logo': 'http://i.imgur.com/AlhNrHz.png'}
            self.epg['FR - BEIN SPORT MAX 5 HD .'] = {'channel_name': 'beIN Sports MAX 5', 'channel_id': 'beINSPORTS5', 'channel_logo': 'http://i.imgur.com/Kw5abIn.png'}
            self.epg['FR - BEIN SPORT MAX 6 HD'] = {'channel_name': 'beIN Sports MAX 6', 'channel_id': 'beINSPORTS6', 'channel_logo': 'http://i.imgur.com/kH0559B.png'}
            self.epg['FR - BEIN SPORT MAX 7 HD'] = {'channel_name': 'beIN Sports MAX 7', 'channel_id': 'beINSPORTS7', 'channel_logo': 'http://i.imgur.com/1hseu21.png'}
            self.epg['FR - BEIN SPORT MAX 8 HD'] = {'channel_name': 'beIN Sports MAX 8', 'channel_id': 'beINSPORTS8', 'channel_logo': 'http://i.imgur.com/WgbJDWT.png'}
            self.epg['FR - BEIN SPORT MAX 9 HD'] = {'channel_name': 'beIN Sports MAX 9', 'channel_id': 'beINSPORTS9', 'channel_logo': 'http://i.imgur.com/FLJbnmT.png'}
            self.epg['FR - BFM SPORT HD'] = {'channel_name': 'BFM Sport', 'channel_id': 'BFMSport', 'channel_logo': 'http://i.imgur.com/ENXQAvd.png'}
            self.epg['FR - FOOT 24 HD'] = {'channel_name': 'Foot+ 24/24', 'channel_id': 'Footplus2424', 'channel_logo': 'http://i.imgur.com/Ozn38ZD.png'}
            self.epg['FR - AB MOTEUR HD'] = {'channel_name': 'AB Moteurs', 'channel_id': 'ABMoteurs', 'channel_logo': 'http://i.imgur.com/Ld0mhbO.png'}
            self.epg['FR - TEVA HD'] = {'channel_name': 'Téva', 'channel_id': 'Teva.fr', 'channel_logo': 'http://i.imgur.com/OSMhqqC.png'}
            self.epg['FR - NRJ 12 HD'] = {'channel_name': 'NRJ 12', 'channel_id': 'NRJ12.fr', 'channel_logo': 'http://i.imgur.com/BDdoSly.png'}
            self.epg['FR - TV 5 MONDE HD'] = {'channel_name': 'TV5 Monde', 'channel_id': 'TV5MONDE', 'channel_logo': 'http://i.imgur.com/MYGq3B5.jpg'}
            self.epg['FR - HD1 HD'] = {'channel_name': 'TF1 Séries Films', 'channel_id': 'HD1.fr', 'channel_logo': 'https://upload.wikimedia.org/wikipedia/fr/thumb/5/5f/TF1_Séries_Films_logo_2018.svg/320px-TF1_Séries_Films_logo_2018.svg.png'}
            self.epg['FR - KTO HD'] = {'channel_name': 'KTO', 'channel_id': 'KTO', 'channel_logo': 'http://i.imgur.com/NWCwsvst.jpg'}
            self.epg['FR - SERIE CLUB HD'] = {'channel_name': 'Série Club', 'channel_id': 'SerieClub.fr', 'channel_logo': 'http://i.imgur.com/Pz1WPCZ.jpg'}
            self.epg['FR - TOONAMI HD'] = {'channel_name': 'Toonami', 'channel_id': 'Toonami', 'channel_logo': 'http://i.imgur.com/Dou5iMu.png'}
            self.epg['FR - DISCOVERY FAMILY HD'] = {'channel_name': 'Discovery Family', 'channel_id': 'DiscoveryFamily', 'channel_logo': 'http://i.imgur.com/1NrMq2j.png'}
            self.epg['FR - DISCOVERY INVESTIGATION HD'] = {'channel_name': 'Discovery Investigation', 'channel_id': 'DiscoveryInvestigationF', 'channel_logo': 'http://i.imgur.com/2IhOal9.png'}
            self.epg['|FR| VICELAND HD'] = {'channel_name': 'Viceland', 'channel_id': 'Viceland', 'channel_logo': 'http://i.imgur.com/5zfidHC.jpg'}
            self.epg['FR - EURONEWS HD'] = {'channel_name': 'Euronews', 'channel_id': 'EuronewsF', 'channel_logo': 'http://i.imgur.com/gp1J2Qn.png'}
            self.epg['FR - LCP HD'] = {'channel_name': 'La Chaine Parlementaire', 'channel_id': 'LCP.fr', 'channel_logo': 'http://i.imgur.com/P0YnHlu.jpg'}
            self.epg['FR - M6 MUSIC'] = {'channel_name': 'M6 Music', 'channel_id': 'M6Music', 'channel_logo': 'http://i.imgur.com/7PrjdEz.png'}
            self.epg['FR - VH1 CLASSIC'] = {'channel_name': 'VH1 Classic', 'channel_id': 'VH1Classic', 'channel_logo': 'http://chanlogos.xmltv.se/classic.vh1.se.png'}

        def find(self, channel):
            return self.epg[channel]

        def channels(self):
            return self.epg.keys()

    user_id = request.args.get('username')
    user_pwd = request.args.get('password')
    m3u = M3uDownload(user_id, user_pwd).get()
    if m3u is None:
        abort(404)
    return M3uParser(m3u).parse()