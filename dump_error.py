import traceback
import sys

def run():
    try:
        import client.main
        client.main.main()
    except Exception as e:
        with open('error.txt', 'w') as f:
            traceback.print_exc(file=f)

if __name__ == "__main__":
    run()
