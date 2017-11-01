#coding: utf-8

import ujson 



class ExampleMsgManager(object):
	def user_join(self, handler, data):
		print 'recv data ', data
		ret = {
				"msg_type": "ack_user_join",
				"msg_id": "124",
				"data":{
				}
			}

		ret = {
		    "body": {
		        "user_info": [
		            {
		                "username": "游客_2867413",
		                "photo": "",
		                "total": "200888",
		                "uid": "1003054"
		            }
		        ],
		        "pre_result": {
		            "second": [
		                {
		                    "matchid": "012204620",
		                    "winid": "1020202",
		                    "stagename": "second",
		                    "awayid": "1020247",
		                    "is_extratime": "0",
		                    "settledresult": "1",
		                    "score": "3:1",
		                    "expect": "0122046",
		                    "is_spotkick": "0",
		                    "homeid": "1020202",
		                    "spotkick": "0:0"
		                },
		                {
		                    "matchid": "012204621",
		                    "winid": "1020258",
		                    "stagename": "second",
		                    "awayid": "1020258",
		                    "is_extratime": "0",
		                    "settledresult": "2",
		                    "score": "0:2",
		                    "expect": "0122046",
		                    "is_spotkick": "0",
		                    "homeid": "1020240",
		                    "spotkick": "0:0"
		                }
		            ],
		            "first": [
		                {
		                    "matchid": "012204610",
		                    "winid": "1020202",
		                    "stagename": "first",
		                    "awayid": "1020214",
		                    "is_extratime": "0",
		                    "settledresult": "1",
		                    "score": "3:2",
		                    "expect": "0122046",
		                    "is_spotkick": "0",
		                    "homeid": "1020202",
		                    "spotkick": "0:0"
		                },
		                {
		                    "matchid": "012204611",
		                    "winid": "1020247",
		                    "stagename": "first",
		                    "awayid": "1020216",
		                    "is_extratime": "1",
		                    "settledresult": "1",
		                    "score": "0:0",
		                    "expect": "0122046",
		                    "is_spotkick": "1",
		                    "homeid": "1020247",
		                    "spotkick": "6:5"
		                },
		                {
		                    "matchid": "012204612",
		                    "winid": "1020240",
		                    "stagename": "first",
		                    "awayid": "1020203",
		                    "is_extratime": "0",
		                    "settledresult": "1",
		                    "score": "2:1",
		                    "expect": "0122046",
		                    "is_spotkick": "0",
		                    "homeid": "1020240",
		                    "spotkick": "0:0"
		                },
		                {
		                    "matchid": "012204613",
		                    "winid": "1020258",
		                    "stagename": "first",
		                    "awayid": "1020258",
		                    "is_extratime": "1",
		                    "settledresult": "2",
		                    "score": "2:2",
		                    "expect": "0122046",
		                    "is_spotkick": "1",
		                    "homeid": "1020209",
		                    "spotkick": "1:4"
		                }
		            ]
		        },
		        "result": [],
		        "stageid": "3",
		        "room_info": {
		            "leaguename": "欧洲杯",
		            "expect": "0122046",
		            "stageid": "3",
		            "title": "欧洲杯决赛",
		            "leagueid": "202",
		            "index": "046",
		            "roomid": "127.0.0.1-9001-1485144115.437057",
		             "nodeid":"127.0.0.1:9001", #节点ID
		            "desc": "当日第46期"
		        },
		        "matches": [
		            {
		                "matchid": "012204630",
		                "home_golds": "0",
		                "awayid": "1020258",
		                "plate_status": "on",
		                "homeleagueid": "202",
		                "awayleagueid": "202",
		                "homelogo": "",
		                "homeleaguename": "欧洲杯",
		                "homename": "比利时",
		                "expect": "0122046",
		                "away_golds": "0",
		                "awaylogo": "",
		                "homeid": "1020202",
		                "awayodds": "4.5",
		                "homeodds": "1.13",
		                "awayname": "列支敦士登",
		                "awayleaguename": "欧洲杯",
		                "result": {}
		            }
		        ],
		        "process_time": "8",
		        "curr_messageid": "2003",
		        "cur_event": [],
		        "expect": "0122046"
		    },
		    "messagetype": "init",
		    "messageid": "2000"
			}
		return ret 

	def user_leave(self, handler, data):
		print 'user leave ', data
		ret = {
			"msg_type": "ack_user_leave",
			"msg_id": "124",
			"data":{
				}
			}
		return ret 