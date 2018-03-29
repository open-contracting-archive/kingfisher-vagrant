import sys
from os import path
import ocdsdata.sources.taiwan
import ocdsdata.sources.canada_buyandsell


def main():

    fetcher1 = ocdsdata.sources.taiwan.TaiwanFetcher()
    fetcher1.run_all()

    fetcher2 = ocdsdata.sources.canada_buyandsell.CanadaBuyAndSellFetcher()
    fetcher2.run_all()


if __name__ == '__main__':
    main()
