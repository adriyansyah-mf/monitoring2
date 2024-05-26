import subprocess
from models.DomainsNotLive import DomainsNotLiveModel
from models.db import engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)

def run_httpx_command(domain):
    command = ["httpx-toolkit", "-u", domain, "-nc", "-sc", "-title"]
    try:
        print(f"Execute HTTPX {domain}")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout.split(" ")
        with open("httpx_log.log", "a") as f:
            f.write(result.stdout)
        return {
            "status_code" : output[1],
            "url":output[0]
        }
    except subprocess.CalledProcessError as e:
        print("Command failed with error:", e)
    except IndexError:
        return False

def main():
    session = Session()
    try:
        with session.begin():
            query = session.query(DomainsNotLiveModel)
            result = session.execute(query)
            for i in result:
                print(i)
                if run_httpx_command(i.domain) == "[200]":
                    session.query(DomainsNotLiveModel).filter(DomainsNotLiveModel.c.id == result.id).delete()
                    session.commit()
                    session.close()


            # if result:
            #     print(f"HTTPX Process with domain {result.domain}")
            #     if run_httpx_command(result.domain) == "[200]":
            #
            #         session.query(DomainsNotLiveModel).filter(DomainsNotLiveModel.c.id == result.id).delete()
            #     session.commit()
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        session.close()




if __name__ == "__main__":
    main()
