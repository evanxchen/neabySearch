class Config:
    # 查詢超時時間（秒）
    QUERY_TIMEOUT = 300
    
    # 查詢結果保存路徑
    RESULTS_PATH = "query_results.json"
    
    # 不同 Form 類型對應的地標分數
    LANDMARK_SCORES = {
       "D": { ## 危老都更
           "001": 7,  # 交通類型分數
           "002": 5,   # 購物類型分數
           "003": 3,
           "004": 0,
           "005": 8,
           "006": 6,
           "007": 4,
           "008": 2,
           "009": 1,
           "010": 0,
           "011": -25,
           "012": -20,
           "013": -20,
           "014": -15,
           "015": -15,
           "016": -10,
           "017": -10,
           "018": -5,
           "019": -5,
           "020": -5,
           "021": -5,
           "022": 0
       },
       "C": {   ## 銷售型土建融
           "001": 10,  # 交通類型分數
           "002": 8,   # 購物類型分數
           "003": 4,
           "004": 0,
           "005": 10,
           "006": 8,
           "007": 6,
           "008": 3,
           "009": 2,
           "010": 0,
           "011": -25,
           "012": -20,
           "013": -20,
           "014": -15,
           "015": -15,
           "016": -10,
           "017": -10,
           "018": -5,
           "019": -5,
           "020": -5,
           "021": -5,
           "022": 0
       }
   }
    # 定義每種地標類型包含的 Google Places types
    PLACE_TYPE_MAPPING = {
        "001": [  # 交通類型
            {
                'case_type': '台鐵站',
                'case_kind': 'A',
                "search_types": ["train_station"],
                "check_types": [
                    ["establishment", "point_of_interest", "train_station"]
                ]
            },
            {
                'case_type': '客運站',
                'case_kind': 'A',
                "search_types": ["bus_station"],
                "check_types": [
                    ["bus_station","transit_station","bus_stop"]
                ]
            }
        ],
        "003": [  # 購物類型
            {
                'case_type': '公車站牌',
                'case_kind': 'A',
                "search_types": ["bus_stop"],
                "check_types": [["bus_station","bus_stop"]
                    
                ]
            }
        ],
        "005": [  # 購物類型
            {
                'case_type': '超級市場',
                'case_kind': 'B',
                "search_types": ["supermarket"],
                "check_types": [["supermarket","grocery_store"],
                                ["point_of_interest","establishment","supermarket","grocery_store","store"]
                    
                ]
            },
            {
                'case_type': '傳統市場',
                'case_kind': 'B',
                "search_types": ["bus_stop"],
                "check_types": [["point_of_interest","market","establishment"]
                ]
            },
            {
                'case_type': '各類商店市集',
                'case_kind': 'B',
                "search_types": ["bus_stop"],
                "check_types": [["point_of_interest","store","establishment"],
                                ["point_of_interest","store","establishment","clothing_store"],
                                ["point_of_interest","store","establishment","electronics_store"],
                                ["point_of_interest","store","establishment","book_store"],
                                ["point_of_interest","store","establishment","home_goods_store"],
                                ["point_of_interest","store","establishment","shoe_store"]
                ]
            }
        ],
        "006": [  # 購物類型
            {
                'case_type': '學校',
                'case_kind': 'B',
                "search_types": ["school"],
                "check_types": [["point_of_interest","establishment","university"],
                                ["point_of_interest","establishment","primary_school"],
                                ["point_of_interest","establishment","secondary_school"]   
                ]
            }
        ],
        "007": [  # 購物類型
            {
                'case_type': '公園',
                'case_kind': 'B',
                "search_types": ["park"],
                "check_types": [["point_of_interest","establishment","park"], 
                                ["point_of_interest","establishment","premise","park"],
                                ["point_of_interest","establishment","tourist_attraction","park"]
                ]
            }
        ],
        "008": [  # 購物類型
            {
                'case_type': '郵局',
                'case_kind': 'B',
                "search_types": ["post_office"],
                "check_types": [["post_office","government_office"], 
                                ["point_of_interest","establishment","post_office"],
                                ["establishment","post_office"]
                ]
            },
            {
                'case_type': '銀行',
                'case_kind': 'B',
                "search_types": ["bank"],
                "check_types": [["bank","point_of_interest","finance", "establishment"]
                ]
            }
        ],
         "009": [  # 購物類型
            {
                'case_type': '球場',
                'case_kind': 'B',
                "search_types": ["post_office"],
                "check_types": [["athletic_field", "sports_activity_location", "stadium"]
                ]
            },
            {
                'case_type': '體育場',
                'case_kind': 'B',
                "search_types": ["bank"],
                "check_types": [["sports_complex", "sports_activity_location", "premise"]
                ]
            },
            {
                'case_type': '廣場',
                'case_kind': 'B',
                "search_types": ["hospital"],
                "check_types": [ ["park", "plaza"]
                ]
            },
             {
                'case_type': '兒童遊樂場',
                'case_kind': 'B',
                "search_types": ["hospital"],
                "check_types": [["playground", "park"]
                ]
            },
             {
                'case_type': '便利超商',
                'case_kind': 'B',
                "search_types": ["hospital"],
                "check_types": [["convenience_store", "store"]
                ]
             },
             {
                'case_type': '地方診所',
                'case_kind': 'B',
                "search_types": ["hospital"],
                "check_types": [["convenience_store", "store"]
                ]
            }
        ]
    }
    # 地標類型與搜尋參數設定
    LANDMARK_TYPES = {
        "001": {  # 交通類型
            "name": "捷運站／台鐵站／客運站／運輸中心（轉運站）1公里內/高鐵車站 2公里內",
            "case_kind":"A",
            "cases": [
                {
                    "case_type": "捷運站",
                    "distance": 1000,
                    "search_methods": {"type": "local_only"}
                    }
                ,
                {
                    "case_type": "台鐵站",
                    "distance": 1000,
                    "search_methods": {
                        "type": "nearby_first",
                        "nearby": {
                            "params": {
                                "includedTypes": ["train_station",],
                                "maxResultCount": 1
                            }
                        },
                        "autocomplete": {
                            "params": {
                                "input": "台鐵",
                                "includedTypes": ["train_station"]
                            }
                        }
                    }
                },
                {
                    "case_type": "客運站",
                    "distance": 1000,
                    "search_methods": {
                        "type": "autocomplete_only",
                        "autocomplete": {
                            "params": {
                                "input": "客運",
                                "includedTypes": ["transit_station", "bus_station"]
                                        }
                                    }
                    }
                },
                {
                    "case_type": "運輸中心(轉運站)",
                    "distance": 1000,
                    "search_methods": {
                        "type": "autocomplete_only",
                        "autocomplete": {
                            "params": {
                                "input": "轉運",
                                "includedTypes": ["transit_station"]
                                        }
                                    }
                                }
                },
                {
                    "case_type": "高鐵站",
                    "distance": 1000,
                    "search_methods": {"type": "local_only"}
                }
            ]
        },
        "002": {  # 交通機能
            "name": "高速公路或快速道路交流道3公里內",
            "case_kind":"A",
            "distance": 3000,
            "cases": [
                {
                    "case_type": "國道交流道",
                    "distance": 3000,
                    "search_methods": {
                        "type": "local_only",
                        "autocomplete": {
                            "params": {
                                "input": "國道交流道",
                                "includedTypes": ["geocode","political"]
                            }
                        }
                    }
                },
                {
                    "case_type": "快速道路交流道",
                    "distance": 3000,
                    "search_methods": {
                        "type": "local_only",
                        "autocomplete": {
                            "params": {
                                "input": "快速道路交流道",
                                "includedTypes": ["geocode","political"]
                            }
                        }
                    }
                }
            ]
        },
        "003": {  #公車站牌
            "name": "公車站牌500公尺內/正面臨路路寬20M(含)以上",
            "case_kind":"A",
            "distance": 500,
            "cases": [
                {
                    "case_type": "公車站牌",
                    "distance": 500,
                    "search_methods": {
                        "type": "nearby_only",
                        "nearby": {
                            "params": {
                                "includedTypes": ["bus_stop"],
                                "maxResultCount": 1,
                                "includedPrimaryTypes": ["bus_station","transit_station","bus_stop"]
                            }
                        }
                    }
                }]
        },
        "005": { #＃＃超級市場
            "name": "超級市場、傳統市場、各類商店市集 1公里內",
            "case_kind":"B",
            "cases": [
                {
                    "case_type": "超級市場",  ##大賣場
                    "distance": 1000,
                    "search_methods": {
                        "type": "autocomplete_only",
                        "autocomplete":{
                            "params": {
                                "input": "好市多",
                                "includedTypes": ["point_of_interest","establishment","warehouse_store","market", "supermarket"],   
                            }
                        }
                    }
                },
                {
                    "case_type": "超級市場",  ##大賣場
                    "distance": 1000,
                    "search_methods": {
                        "type": "autocomplete_only",
                        "autocomplete":{
                            "params": {
                                "input": "家樂福",
                                "includedTypes": ["point_of_interest","establishment","warehouse_store","market", "supermarket"]
                            }
                        }
                    }
                },
                {
                    "case_type": "超級市場",  ##大賣場
                    "distance": 1000,
                    "search_methods": {
                        "type": "autocomplete_only",
                        "autocomplete":{
                            "params": {
                                "input": "大潤發",
                                "includedTypes": ["warehouse_store", "supermarket"]
                            }
                        }
                    }
                },
                {
                    "case_type": "超級市場",  ##大賣場
                    "distance": 1000,
                    "search_methods": {
                        "type": "autocomplete_only",
                        "autocomplete":{
                            "params": {
                                "input": "愛買",
                                "includedTypes": ["market", "supermarket"]  
                            }
                        }
                    }
                },
                {
                    "case_type": "超級市場",  ##大賣場
                    "distance": 1000,
                    "search_methods": {
                        "type": "autocomplete_only",
                        "autocomplete":{
                            "params": {
                                "input": "大買家",
                                "includedTypes": ["market", "supermarket"]  
                            }
                        }
                    }
                },
                {
                    "case_type": "超級市場",  ##大賣場
                    "distance": 1000,
                    "search_methods": {
                        "type": "autocomplete_only",
                        "autocomplete":{
                            "params": {
                                "input": "迪卡儂",
                                "includedTypes": ["warehouse_store","market", "supermarket"]
                            }
                        }
                    }
                },
                {
                    "case_type": "傳統市場",
                    "distance": 1000,
                    "search_methods": {
                        "type": "autocomplete_only",
                        "autocomplete": {
                            "params": {
                                "input": "市場",
                                "includedTypes": ["point_of_interest","market","establishment", "tourist_attraction"]  ##不包含餐廳跟小吃店
                            }
                        }
                    }
                },
                {
                    "case_type": "各類商店市集",  ##包含超市跟其他商店
                    "distance": 1000,
                    "search_methods": {
                        "type": "nearby_only",
                        "nearby": {
                            "params": {
                                "includedTypes": ["supermarket","store", "grocery_store"],
                                "maxResultCount": 3,
                                "includedPrimaryTypes": ["supermarket","grocery_store"],
                                "excludedPrimaryTypes":["convenience_store", "restaurant", "deli"]
                    }
                        }
                    }
                },
                {
                    "case_type": "各類商店市集",  ##包含超市跟其他商店
                    "distance": 1000,
                    "search_methods": {
                        "type": "nearby_only",
                        "nearby": {
                            "params": {
                                "includedTypes": ["store", "home_goods_store", "hardware_store", "electronics_store"],
                                "maxResultCount": 3,
                                "includedPrimaryTypes": ["store"],
                                "excludedPrimaryTypes":["convenience_store", "restaurant", "deli"] 
                    }
                        }
                    }
                }
            ]
        },
        "006": {
            "name": "學校或政府機關1公里內/ 科學園區、工業區等聚落3公里內",
            "case_kind":"B",
            "cases": [
                {
                    "case_type": "學校",
                    "distance":1000,
                    "search_methods": {
                        "type": "nearby_only",
                        "nearby": {
                            "params": {
                                "includedTypes": ["university","primary_school","secondary_school"],
                                "maxResultCount": 2,
                                "includedPrimaryTypes": ["university","primary_school","secondary_school"],
                                "excludedPrimaryTypes":["store","market","child_care_agency","parking"]
                            }
                        }
                    }
                },
                {
                    "case_type": "政府機構",
                    "distance":1000,
                    "search_methods": {
                        "type": "local_only"
                    }
                },
                {
                    "case_type": "科學園區",
                    "distance":3000,
                    "search_methods": {
                        "type": "autocomplete_only",
                        "autocomplete": {
                            "params": {
                                "input": "科學園區",
                                "includedTypes": ["geocode","neighborhood","political"],
                            }
                        }
                    }
                },
                {
                    "case_type": "工業區",
                    "distance":3000,
                    "search_methods": {
                        "type": "autocomplete_only",
                        "autocomplete": {
                            "params": {
                                "input": "工業區",
                                "includedTypes": ["geocode","neighborhood","political"],
                            }
                        }
                    }
                }
            ]
        },
        "007":{
            "name": "中大型公園(200坪)以上、百貨公司、大型購物中心1公里內",
            "case_kind":"B",
            "cases": [
                {
                    "case_type": "公園",
                    "distance":1000,
                    "search_methods": {
                        "type": "nearby_only",
                        "nearby": {
                            "params": {
                                "includedTypes": ["park"],
                                "maxResultCount": 3,
                                "includedPrimaryTypes": ["park", "tourist_attraction"],
                                "excludedPrimaryTypes":["store","market"]
                            }
                        }
                    }
                },
                {
                    "case_type": "百貨公司",
                    "distance":1000,
                    "search_methods": {
                        "type": "local_only"
                            }
                }
            ]
        },
        "008": {
            "name": "服務性設施（含郵局、銀行、醫院)1公里內",
            "case_kind":"B",
            "cases": [
                {
                    "case_type": "郵局",
                    "distance": 1000,
                    "search_methods": {
                        "type": "autocomplete_only",
                        "autocomplete": {
                            "params": {
                                "input": "郵局",
                                "includedTypes":  ["post_office","government_office"],
                            }
                        }
                    }
                },
                {
                    "case_type": "銀行",
                    "distance": 1000,
                    "search_methods": {
                        "type": "nearby_only",
                        "nearby": {
                            "params": {
                                "includedTypes": ["bank"],
                                "maxResultCount": 1,
                                "includedPrimaryTypes": ["bank", "finance"]
                                
                            }
                        }
                    }
                },
                {
                    "case_type": "醫院",
                    "distance": 1000,
                    "search_methods": {
                        "type": "local_only",
                        }
                }
            ]
        },
        "009":{
            "name": '遊憩設施(含兒童遊樂場、大型球場、體育場、廣場等)1公里內；便利超商、小型公園(100坪以下)或地方診所500公尺內',
            "case_kind": "B",
            "cases": [
                {
                    "case_type": "球場",
                    "distance": 1000,
                    "search_methods": {
                        "type": "autocomplete_only",
                        "autocomplete": {
                            "params": {
                                "input": "場",
                                "includedTypes":  ["athletic_field", "sports_activity_location", "stadium"],
                            }
                        }
                    }
                },
                {
                    "case_type": "體育場",
                    "distance": 1000,
                    "search_methods": {
                        "type": "autocomplete_only",
                        "autocomplete": {
                            "params": {
                                "input": "體育館",
                                "includedTypes":  ["sports_complex", "sports_activity_location", "premise"],
                            }
                        }
                    }
                },
                {
                    "case_type": "廣場",
                    "distance": 1000,
                    "search_methods": {
                        "type": "autocomplete_only",
                        "autocomplete": {
                            "params": {
                                "input": "廣場",
                                "includedTypes":  ["park", "plaza"],
                            }
                        }
                    }
                },
            {
                    "case_type": "兒童遊樂場",
                    "distance": 1000,
                    "search_methods": {
                        "type": "autocomplete_only",
                        "autocomplete": {
                            "params": {
                                "input": "兒童",
                                "includedTypes":  ["playground", "park"],
                            }
                        }
                    }
            },
            {
                    "case_type": "便利超商",
                    "distance": 500,
                    "search_methods": {
                        "type": "nearby_first",
                        "nearby": {
                            "params": {
                                "includedTypes": ["convenience_store"],
                                "maxResultCount": 1,
                                "includedPrimaryTypes": ["convenience_store"],
                                "excludedPrimaryTypes":["supermarket"],
                                
                                
                            },
                        "autocomplete": {
                            "params": {
                                "input": "美廉社",
                                "includedTypes":   ["convenience_store", "store"]
                            }
                        }
                    }
                }
            },
            {
                    "case_type": "地方診所",
                    "distance": 500,
                    "search_methods": {
                        "type": "nearby_first",
                        "nearby": {
                            "params": {
                                "includedTypes": ["doctor","dental_clinic"],
                                "maxResultCount": 1,
                                "includedPrimaryTypes": ["doctor","dental_clinic"],
                                "excludedPrimaryTypes":["hospital"]   
                            }
                        }
                    }
                }
            ]        
        },
        "011": {
            "name": "火葬場、墳墓(福地)(200公尺內)",
            "case_kind":"C",
            "cases": [
                {
                    "case_type": "火化場",
                    "distance": 200,
                    "search_methods": {
                        "type": "local_only"
                    }
                },
                {
                    "case_type": "墳墓",
                    "distance": 200,
                    "search_methods": {
                        "type": "autocomplete_only",
                        "nearby": {
                            "params": {
                                "includedTypes": ["cemetery",],
                                "maxResultCount": 1
                            }
                        },
                        "autocomplete": {
                            "params": {
                                "input": "墓",
                                "includedTypes": ["cemetery"]
                            }
                        }
                    }
                }
            ]
        },
        "012": {
            "name": "焚化爐(200公尺內)",
            "case_kind":"C",
            "cases": [
                {
                    "case_type": "焚化爐",
                    "distance": 200,
                    "search_methods": {
                        "type": "local_only"
                    }
                }
            ]
        },
        "013": {
            "name": "殯儀館(100公尺內)",
            "case_kind":"C",
            "cases": [
                {
                    "case_type": "殯儀館",
                    "distance": 200,
                    "search_methods": {
                        "type": "nearby_only",
                        "nearby": {
                            "params": {
                                "includedTypes": ["funeral_home",],
                                "maxResultCount": 1,
                                "includedPrimaryTypes": ["funeral_home"]
                            }
                        }
                    }
                }
            ]
        },
        "014": {
            "name": "特種行業(八大行業、酒店、遊藝場、PUB等場所)50公尺內",
            "case_kind":"C",
            "cases": [
                {
                    "case_type": "遊藝場",
                    "distance": 50,
                    "search_methods": {
                        "type": "nearby_only",
                        "nearby": {
                            "params": {
                                "includedTypes": ["video_arcade"],
                                "maxResultCount": 1,
                                "includedPrimaryTypes": ["amusement_park"]
                            }
                        }
                    }
                },
                {
                    "case_type": "PUB、夜店",
                    "distance": 50,
                    "search_methods": {
                        "type": "nearby_only",
                        "nearby": {
                            "params": {
                                "includedTypes": ['pub', 'dance_hall', "night_club"],
                                "maxResultCount": 1
                            }
                        }
                    }
                }
            ]
        },
        "015": {
            "name": "高壓電塔、變電所、發電廠、氣體製造廠(50公尺)",
            "case_kind":"C",
            "cases": [
                {
                    "case_type": "高壓電塔",
                    "distance": 50,
                    "search_methods": {
                        "type": "local_only"
                    }
                },
                {
                    "case_type": "變電所",
                    "distance": 50,
                    "search_methods": {
                        "type": "autocomplete_only",
                         "autocomplete": {
                            "params": {
                                "input": "變電所",
                                "includedTypes": ["government_office", "establishment", "point_of_interest"]
                            }
                        }
                    }
                },
                {
                    "case_type": "發電廠",  ##包含風力發電
                    "distance": 50,
                    "search_methods": {
                        "type": "local_only",
                         
                    }
                },
                {
                    "case_type": "氣體製造廠",  
                    "distance": 50,
                    "search_methods": {
                        "type": "local_only",
                    }
                }
            ]
        },
        "016": {
            "name": "加油站、液化石油氣分裝場(50公尺內)",
            "case_kind":"C",
            "cases": [
                {
                    "case_type": "加油站",
                    "distance": 50,
                    "search_methods": {
                        "type": "nearby_only",
                        "nearby": {
                            "params": {
                                "includedTypes": ["gas_station"],
                                "maxResultCount": 1,
                                "includedPrimaryTypes": ["gas_station"]
                            }
                        }
                    }
                },
                {
                    "case_type": "液化石油分裝場",
                    "distance": 50,
                    "search_methods": {
                        "type": "local_only"
                    }
                }
            ]
        },
        "017": {
            "name": "瓦斯行、瓦斯分裝場、瓦斯槽(50公尺內)",
            "case_kind":"C",
            "cases": [
                {
                    "case_type": "瓦斯行",
                    "distance": 50,
                    "search_methods": {
                        "type": "autocomplete_only",
                        "autocomplete": {
                            "params": {
                                "input": "瓦斯行",
                                "includedTypes": ["store", "establishment", "point_of_interest"]
                            }
                    }
                }
                },
                {
                    "case_type": "瓦斯分裝場",
                    "distance": 50,
                    "search_methods": {
                        "type": "autocomplete_only",
                         "autocomplete": {
                            "params": {
                                "input": "煤氣",
                                "includedTypes": ["government_office", "establishment", "point_of_interest"]
                            }
                        }
                    }
                },
                    {
                    "case_type": "瓦斯槽",  ## not yet 
                    "distance": 50,
                    "search_methods": {
                        "type": "autocomplete_only",
                         "autocomplete": {
                            "params": {
                                "input": "瓦斯槽",
                                "includedTypes": ["government_office", "establishment", "point_of_interest"]
                            }
                        }
                    }
                },
                {
                    "case_type": "發電廠",  ##包含風力發電
                    "distance": 50,
                    "search_methods": {
                        "type": "local_only",
                         
                    }
                },
                {
                    "case_type": "氣體製造廠",  
                    "distance": 50,
                    "search_methods": {
                        "type": "local_only",
                         
                    }
                }
            ]
        },
        "018": {
            "name": "宮廟、神壇(50公尺內)",
            "case_kind":"C",
            "cases": [
                {
                    "case_type": "宮廟",
                    "distance": 50,
                    "search_methods": {
                        "type": "autocomplete_only",
                        "autocomplete": {
                            "params": {
                                "input": "寺",
                                "includedTypes": ["place_of_worship"]
                            }
                    }
                }
                },
                {
                    "case_type": "宮廟",
                    "distance": 50,
                    "search_methods": {
                        "type": "autocomplete_only",
                         "autocomplete": {
                            "params": {
                                "input": "廟",
                                "includedTypes": ["place_of_worship"]
                            }
                        }
                    }
                },
                    {
                    "case_type": "宮廟",
                    "distance": 50,
                    "search_methods": {
                        "type": "autocomplete_only",
                         "autocomplete": {
                            "params": {
                                "input": "宮",
                                "includedTypes": ["place_of_worship"]
                            }
                        }
                    }
                    },
                    {
                    "case_type": "神壇",
                    "distance": 50,
                    "search_methods": {
                        "type": "autocomplete_only",
                         "autocomplete": {
                            "params": {
                                "input": "壇",
                                "includedTypes": ["place_of_worship"]
                            }
                        }
                    }
                },
                    {
                    "case_type": "宮廟",
                    "distance": 50,
                    "search_methods": {
                        "type": "autocomplete_only",
                         "autocomplete": {
                            "params": {
                                "input": "四面佛",
                                "includedTypes": ["place_of_worship"]
                            }
                        }
                    }
                }
            ]
        },
        "019": {
            "name": "工廠(50公尺內)",
            "case_kind":"C",
            "cases": [
                {
                    "case_type": "工廠",
                    "distance": 50,
                    "search_methods": {
                        "type": "local_only"
                    }
                }
                ]
        },
        "020": {
            "name": "垃圾場、資源回收場(50公尺內)",
            "case_kind":"C",
            "cases": [
                {
                    "case_type": "垃圾場",
                    "distance": 50,
                    "search_methods": {
                     "type": "autocomplete_only",
                         "autocomplete": {
                            "params": {
                                "input": "掩埋場",
                                "includedTypes": ["establishment", "point_of_interest"]
                            }
                        }
                    }
                },
                {
                    "case_type": "資源回收場",
                    "distance": 50,
                    "search_methods": {
                     "type": "autocomplete_only",
                         "autocomplete": {
                            "params": {
                                "input": "回收場",
                                "includedTypes": ["establishment", "point_of_interest"]
                            }
                        }
                    }
                }
            ]
        },
        "021": {
            "name": "鐵道(50公尺內)",
            "case_kind":"C",
            "cases": [
                {
                    "case_type": "鐵道",
                    "distance": 50,
                    "search_methods": {
                     "type": "shap_only"
                    }
                }
            ]
    }
}
