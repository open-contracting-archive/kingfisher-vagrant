import sys
from os import path
import ocdsdata.sources.taiwan



def main():

    fetcher = ocdsdata.sources.taiwan.TaiwanFetcher()
    fetcher.run_all()



if __name__ == '__main__':
    main()
