import requests
import os
import csv


class Test:
    def __init__(self, strategy):
        self.short = 1
        self.long = 1

        self.strategy = strategy
        self.request_params = {}
        self.best_params = {"short": -1, "long": -1, "profit": -1}

    def make_params(self):
        strat = strategy_params[self.strategy]
        compiled_params = default_request_params
        compiled_params["data"]["gekkoConfig"][self.strategy] = strat
        compiled_params["data"]["gekkoConfig"][self.strategy]["short"] = self.short
        compiled_params["data"]["gekkoConfig"][self.strategy]["long"] = self.long
        compiled_params["data"]["gekkoConfig"]["tradingAdvisor"]["method"] = self.strategy
        self.request_params = compiled_params

    def execute(self):
        for s in range(1, 50, 1):
            self.short = s
            for l in range(1, 50, 1):
                self.long = l

                self.make_params()
                response = self.send_request()
                self.parse_response(response)

    def send_request(self):
        r = requests.post(self.request_params['url'], json=self.request_params['data'], verify=False,
                          auth=(self.request_params['user'], self.request_params['pass']))
        if r.status_code != 200:
            raise Exception("response was not 200", r.text)
        return r

    def parse_response(self, response):
        report = response.json()["report"]
        if report["profit"] > self.best_params["profit"]:
            self.best_params = {"short": self.short, "long": self.long, "profit": report["profit"]}
        print(self.best_params)


def main():
    test = Test("DEMA")
    test.execute()


strategy_params = {"DEMA": {"short": 10, "long": 21, "thresholds": {"down": -0.025, "up": 0.025}}}

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
                    "backtest": {"daterange": {"from": "2017-11-13T02:05:00Z",
                                               "to": "2017-12-14T03:05:00Z"}
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
