import glob
import json
import time
from json import JSONEncoder


def process_time(str_value):
    year = int(str_value[0:4])
    month = int(str_value[5:7])
    day = int(str_value[8:10])
    hour = int(str_value.split("T")[1][0:2])
    minute = int(str_value.split("T")[1][3:5])
    second = int(str_value.split("T")[1][6:8])
    jsonstring = JSONEncoder().encode({
        'Year': year,
        'Month': month,
        'Day': day,
        'Hour': hour,
        'Minute': minute,
        'Second': second
    })
    return jsonstring


def excel_time_stamp(json_t):
    year = json_t['Year']
    month = json_t['Month']
    day = json_t['Day']
    hour = json_t['Hour']
    minute = json_t['Minute']
    seconds = json_t['Second']
    return str(year) + "-" + str(month) + "-" + str(day) + " " + str(hour) + ":" + str(minute) + ":" + str(seconds)


def time_python_format(str_value):
    year = int(str_value[0:4])
    month = int(str_value[5:7])
    day = int(str_value[8:10])
    hour = int(str_value.split("T")[1][0:2])
    minute = int(str_value.split("T")[1][3:5])
    seconds = int(str_value.split("T")[1][6:8])
    t = (year, month, day, hour, minute, seconds, 0, 0, -1)
    secs = time.mktime(t)
    return secs


def check_times(json_t1, json_t2):
    return_value = True
    if not (json_t1['Year'] == json_t2['Year'] and json_t1['Month'] == json_t2['Month'] and json_t1['Day'] == json_t2[
            'Day']):
        return_value = False
    return return_value


def write_to_file(str_value):
    tours_f = open("intrigo.json", "a")
    tours_f.write(str_value)
    tours_f.close()


def check_tour_length(start_time, end_time):
    if time_python_format(end_time) - time_python_format(start_time) > 30 * 60:
        return True
    else:
        return False


tours = open("intrigo.json", "w")
tours.write("[\n")
tours.close()


# open file
firstTour = True
files = glob.glob("/shared_vm/all/intrigo_logs")
line_number = 0
main_json = ""
for f in files:
    with open(f) as opened_file:
        for line in opened_file:
            main_json += line.rstrip()

parsed_input = json.loads(main_json)

avoid_devices = ['afd55e19bb104b40']
tablets = dict()
games = dict()
finished_games = []
current_game = dict()
stops = []
last_good_timestamp = dict()
last_good_timestamp_str = dict()

for evento in parsed_input['events']:
    event = evento['event']
    device_id = event['device_id']
    if device_id not in avoid_devices:
        if device_id in tablets:
            if current_game[device_id] in last_good_timestamp and time_python_format(event['timestamp']) - \
                    last_good_timestamp[current_game[device_id]] < 60 * 30:
                last_good_timestamp[current_game[device_id]] = time_python_format(event['timestamp'])
                last_good_timestamp_str[current_game[device_id]] = event['timestamp']
        if event['type'] == "NEW_GAME_STARTED":
            started = event['timestamp']
            if device_id in tablets:
                if tablets[device_id]:
                    device_id = device_id
                    ended = ""
                    jsonPercorso = JSONEncoder().encode({
                        'tablet': device_id,
                        'Started': json.loads(process_time(current_game[device_id].split("::")[0])),
                        'Ended': json.loads(
                            process_time(last_good_timestamp_str[current_game[device_id]].split("::")[0])),
                        'Stops': json.loads(json.dumps(games[current_game[device_id]])),
                        'game_win': False
                    })
                    if check_tour_length(current_game[device_id].split("::")[0],
                                         last_good_timestamp_str[current_game[device_id]].split("::")[0]):
                        finished_games.append(jsonPercorso)
                    del games[current_game[device_id]]

            current_game[device_id] = started + "::" + device_id
            games[current_game[device_id]] = []
            tablets[device_id] = True
            last_good_timestamp[current_game[device_id]] = time_python_format(event['timestamp'])
            last_good_timestamp_str[current_game[device_id]] = event['timestamp']
        elif event['type'] == "MARKER_DETECTED":
            if device_id in tablets and tablets[device_id]:
                jsonTourStop = JSONEncoder().encode({
                    'Time': json.loads(process_time(event['timestamp'])),
                    'Room': {
                        'RoomName': event['args']['roomName'],
                        'MarkerId': 0
                    }
                })
                games[current_game[device_id]].append(json.loads(jsonTourStop))

                # games[current_game[device_id]].append(event)
                line_number += 1
        elif event['type'] == "GAME_ENDED_WIN":
            if device_id in tablets and tablets[device_id]:
                tablets[device_id] = False
                # print games[event['device_id']]
                jsonPercorso = JSONEncoder().encode({
                    'tablet': device_id,
                    'Started': json.loads(process_time(current_game[device_id].split("::")[0])),
                    'Ended': json.loads(process_time(last_good_timestamp_str[current_game[device_id]].split("::")[0])),
                    'Stops': json.loads(json.dumps(games[current_game[device_id]])),
                    'game_win': True
                })

                if check_tour_length(current_game[device_id].split("::")[0],
                                     last_good_timestamp_str[current_game[device_id]].split("::")[0]):
                    finished_games.append(jsonPercorso)
                del games[current_game[device_id]]
        elif event['type'] == "GAME_ENDED__NO_WIN":
            if device_id in tablets and tablets[device_id]:
                tablets[device_id] = False
                # print games[event['device_id']]
                jsonPercorso = JSONEncoder().encode({
                    'tablet': device_id,
                    'Started': json.loads(process_time(current_game[device_id].split("::")[0])),
                    'Ended': json.loads(process_time(last_good_timestamp_str[current_game[device_id]].split("::")[0])),
                    'Stops': json.loads(json.dumps(games[current_game[device_id]])),
                    'game_win': False
                })

                if check_tour_length(current_game[device_id].split("::")[0],
                                     last_good_timestamp_str[current_game[device_id]].split("::")[0]):
                    finished_games.append(jsonPercorso)
                del games[current_game[device_id]]

for game in games:
    jsonPercorso = JSONEncoder().encode({
        'tablet': game.split("::")[1],
        'Started': json.loads(process_time(game.split("::")[0])),
        'Ended': json.loads(process_time(game.split("::")[0])),
        'Stops': json.loads(json.dumps(games[game])),
        'percorsoOk': False
    })
    finished_games.append(jsonPercorso)

rooms = ["staffarda", "acaia_1", "acaia_2", "acaia_4", "acaia_5", "stemmi", "fibellona", "terrecotte", "acaia_6",
         "acaia_7", "acaia_8", "acaia_3", "torre_tesori_0", "biglietteria", "guidobono", "guardie", "feste_1",
         "torre_tesori_1", "stagioni", "madama_reale", "camera_nuova", "senato", "gabinetto_rotondo", "veranda_nord",
         "veranda_sud", "feste_2", "feste_3", "fiori", "lapidario_1", "lapidario_3", "lapidario_4", "depositi_1",
         "depositi_2", "torre_tesori_-1", "ceramiche_1", "ceramiche_9", "avori_1", "ceramiche_2", "ceramiche_3",
         "ceramiche_4", "ceramiche_5", "ceramiche_6", "ceramiche_7", "ceramiche_8", "avori_2"]

rooms_dict = {'biglietteria': 'biglietteria',
              'staffarda': 'staffarda',
              'acaia_1': 'acaia_1',
              'acaia_2': 'acaia_2',
              'acaia_3': 'acaia_3',
              'torre_tesori_0': 'torre_tesori_0',
              'acaia_5': 'acaia_5',
              'acaia_6': 'acaia_6',
              'acaia_8': 'acaia_8',
              'fibellona': 'fibellona',
              'stemmi': 'stemmi',
              'guidobono': 'guidobono',
              'camera_nuova': 'camera_nuova',
              'feste_1': 'feste', 'feste_2': 'feste', 'feste_3': 'feste',
              'torre_tesori_1': 'torre_tesori_1',
              'guardie': 'guardie',
              'veranda_nord': 'veranda_nord',
              'veranda_sud': 'veranda_sud',
              'ceramiche_1': 'ceramiche', 'ceramiche_2': 'ceramiche', 'ceramiche_3': 'ceramiche',
              'ceramiche_4': 'ceramiche', 'ceramiche_5': 'ceramiche', 'ceramiche_6': 'ceramiche',
              'ceramiche_7': 'ceramiche', 'ceramiche_8': 'ceramiche', 'ceramiche_9': 'ceramiche',
              'avori_1': 'avori', 'avori_2': 'avori',
              'lapidario_1': 'lapidario_1',
              'lapidario_3': 'lapidario_3',
              'lapidario_4': 'lapidario_4',
              'torre_tesori_-1': 'torre_tesori_-1',
              'depositi_1': 'depositi', 'depositi_2': 'depositi'}

room_names = ['biglietteria', 'staffarda', 'acaia_1', 'acaia_2', 'acaia_3', 'torre_tesori_0', 'acaia_5',
              'acaia_6', 'acaia_8', 'fibellona', 'stemmi', 'guidobono', 'camera_nuova', 'feste', 'torre_tesori_1',
              'guardie', 'veranda_nord', 'veranda_sud', 'ceramiche', 'avori', 'lapidario_1', 'lapidario_3',
              'lapidario_4', 'torre_tesori_-1', 'depositi']

room_hits = dict()
serious_csv = open("intrigo.csv", "w")
serious_csv.write("game,tablet,started,ended")
for room in rooms:
    serious_csv.write("," + room)
serious_csv.write("\n")
game_number = 0
for game in finished_games:
    room_hits.clear()
    if not firstTour:
        write_to_file(",\n" + game)
    else:
        firstTour = False
        write_to_file(game)
    game_json = json.loads(game)
    stops = game_json['Stops']
    if len(stops) > 0.2 * len(room_names):
        # informazioni sulla partita
        startedTime = excel_time_stamp(game_json['Started'])
        endedTime = excel_time_stamp(game_json['Ended'])
        serious_csv.write(str(game_number) + "," + game_json['tablet'] + "," + startedTime + "," + endedTime)

        # Controllo le stanze dove e passato l'utente
        for stop in stops:
            if stop['Room']['RoomName'] in rooms:
                room_hits[stop['Room']['RoomName']] = 1
        for room in rooms:
            if room in room_hits:
                serious_csv.write(',1')
            else:
                serious_csv.write(',0')
        serious_csv.write('\n')
        game_number += 1
write_to_file("\n]")
