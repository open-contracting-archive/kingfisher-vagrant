import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
import ocdsdata.sources.taiwan



def main():

    fetcher = ocdsdata.sources.taiwan.TaiwanFetcher()
    fetcher.run_all()



if __name__ == '__main__':
    main()
