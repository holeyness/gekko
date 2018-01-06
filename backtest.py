import requests
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import csv

class Test:
    def __init__(self, strategy):
        self.short = 1
        self.long = 1
        self.signal = 9
        self.results = []
        self.sample_result = {}

        self.strategy = strategy
        self.request_params = {}
        self.best_params = {"short": -1, "long": -1, "signal": -1, "profit": -1}

    def make_params(self):
        strat = strategy_params[self.strategy]
        compiled_params = default_request_params
        compiled_params["data"]["gekkoConfig"][self.strategy] = strat
        compiled_params["data"]["gekkoConfig"][self.strategy]["short"] = self.short
        compiled_params["data"]["gekkoConfig"][self.strategy]["long"] = self.long
        compiled_params["data"]["gekkoConfig"][self.strategy]["signal"] = self.signal
        compiled_params["data"]["gekkoConfig"]["tradingAdvisor"]["method"] = self.strategy
        self.request_params = compiled_params

    def execute(self):
        for sig in range(1, 20, 2):
            self.signal = sig
            for s in range(1, 60, 2):
                self.short = s
                for l in range(1, 60, 2):
                    print("Current params: " + str(s) + " " + str(l) + " " + str(sig))
                    self.long = l

                    self.make_params()
                    response = self.send_request()
                    self.parse_response(response)
        self.write_to_csv()
        print(self.best_params)

    def send_request(self):
        r = requests.post(self.request_params['url'], json=self.request_params['data'], verify=False,
                          auth=(self.request_params['user'], self.request_params['pass']))
        if r.status_code != 200:
            raise Exception("response was not 200", r.text)
        return r

    def parse_response(self, response):
        report = response.json()["report"]
        self.sample_result = report

        list_to_write = [self.short, self.long, self.signal]
        list_to_write.extend(report.values())
        self.results.append(list_to_write)

        if report["profit"] > self.best_params["profit"]:
            self.best_params = {"short": self.short, "long": self.long, "signal": self.signal, "profit": report["profit"]}
            print(self.best_params)

    def write_to_csv(self):
        with open(self.strategy + ".csv", "w") as csv_file:
            writer = csv.writer(csv_file, 'excel')
            header_row = ["short", "long", "signal"]
            header_row.extend(self.sample_result.keys())
            writer.writerow(header_row)
            for line in self.results:
                writer.writerow(line)

def main():
    test = Test("MACD")
    test.execute()


strategy_params = {"MACD": {"short": 10, "long": 21, "signal": 9, "thresholds": {"down": -0.025, "up": 0.025}}}

gekko_params = {
    "gekkoConfig": {"watch": {"exchange": "gdax",
                              "currency": "USD",
                              "asset": "BTC"
                              },
                    "paperTrader": {"feeMaker": 0.25,
                                    "feeTaker": 0.25,
                                    "feeUsing": "maker",
                                    "slippage": 0.05,
                                    "simulationBalance": {
                                        "asset": 0,
                                        "currency": 1000},
                                    "reportRoundtrips": True,
                                    "enabled": True
                                    },
                    "tradingAdvisor": {"enabled": True,
                                       "method": "MACD",
                                       "candleSize": 60,
                                       "historySize": 10
                                       },
                    "backtest": {"daterange": {"from": "2017-12-12T02:05:00Z",
                                               "to": "2017-12-13T03:05:00Z"}
                                 },
                    "performanceAnalyzer": {"riskFreeReturn": 2,
                                            "enabled": True}
                    },
    "data": {"candleProps": ["close", "start"],
             "indicatorResults": True,
             "report": True,
             "roundtrips": True,
             "trades": True}}

default_request_params = {"url": "https://gekko.ianluo.com/api/backtest",
                          "data": gekko_params,
                          "user": os.environ['GEKKO_USER'],
                          "pass": os.environ['GEKKO_PASS']}

if __name__ == "__main__":
    main()
