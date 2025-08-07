from bsor.Bsor import make_bsor, make_info
from bsor.Scoring import calc_stats
import logging
#from bsor.ReeSaber import make_tricksreplay;

import faulthandler

if __name__ == '__main__':
    import os

    faulthandler.enable()
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info('Started')

    # example, read basic info from bsor file
    filename = 'D:/_TMP/reesaber.bsor'
    #filename = 'D:/_TMP/easy.bsor'
    #filename = 'C:/SteamGames/steamapps/common/Beat Saber/UserData/BeatLeader/Replays/76561198026425351-Pounce-ExpertPlus-Standard-901BF0BC525B69A341C307E9AC29C37F145389D8-1722867256.bsor'
    print(f'File name :    {os.path.basename(filename)}')

    from bsor.BsorUtil import *
    thingy = 1

    if thingy == 1:
        with open(filename, "rb") as f:
            print("make")
            m = make_bsor(f)
            #m.info.playerId = '76561198026425351'
            #m.info.playerName = 'Schippi'
            print("write to file")
            try:
                with open('D:/_TMP/easy_Schippi011.bsor', 'wb') as fo:
                    m.write(fo)
                with open('D:/_TMP/easy_Schippi011.bsor', 'rb') as fo:
                    m2 = make_bsor(fo)
                    m2.info.playerId = '76561198026425351'

            except Exception as e:
                print(e)
                raise e
            with open('D:/_TMP/bin_only.bin', 'wb') as fo:
                m.user_data[0].write(fo)

            stats = calc_stats(m)
            print(f'BSOR Version:  {m.file_version}')
            #this is error: m.file_version = 256
            print(f'BSOR magic:  {m.magic_number}')
            print(f'BSOR notes: {len(m.notes)}')
            print(f'BSOR stats: {stats}')
            with open('D:/_TMP/replay.json', 'w') as fi:
                fi.write(str(m))
            with open('D:/_TMP/easy_Schippi022.bsor', 'wb') as fo:
                m.write(fo)
            print(f'BSOR done')

    if thingy ==2:
        my_playlist = unplayed_list(unplayed_player=76561198026425351, count=1200, stars_from=4, stars_to=10)
        with open('D:/_TMP/76561198026425351.bplist', 'w') as f:
            f.write(json.dumps(my_playlist, indent=2))
    if thingy ==3:
        my_playlist = clan_playlist('GER', count=60, stars_from=4, stars_to=10, include_to_hold=False, unplayed_player=76561198026425351)
        with open('D:/_TMP/76561198026425351.bplist', 'w') as f:
            f.write(json.dumps(my_playlist, indent=2))

    if thingy == 4:
        createStatsDB(76561198026425351, 'D:/_TMP/76561198026425351.db')


    #print(my_playlist)1.157.900 Bytes1.157.895 Bytes
