"""(Highly WIP) Example Workload to stress WebUI with python requests."""
from utils.conf import cfme_performance
from utils.grafana import get_default_dashboard_url
from utils.log import logger
from utils.ssh import SSHClient
from requests.auth import HTTPBasicAuth
import requests
import time


def dump_r(r):
    logger.info("==================")
    logger.info("------")
    logger.info("r:")
    logger.info(r)
    #logger.info("------")
    #logger.info("r.text:")
    #logger.info(r.text)
    logger.info("------")
    logger.info("r.headers:")
    logger.info(r.headers)
    logger.info("------")
    logger.info("r.request.headers:")
    logger.info(r.request.headers)
    logger.info("------")
    logger.info("==================")


#@pytest.mark.usefixtures('generate_version_files')
def test_navigate_explorer():
    """Initial Example Workload, Add Provider, turn on some things, initiate navigations on the
    WebUI from python.  Currently lets disable cleaning the appliance etc."""
    from_ts = int(time.time() * 1000)
    ssh_client = SSHClient()

    # clean_appliance(ssh_client)

    cfme_ip = cfme_performance['appliance']['ip_address']
    cfme_web_ui_user = cfme_performance['appliance']['web_ui']['username']
    cfme_web_ui_password = cfme_performance['appliance']['web_ui']['password']

    url = "https://{}/".format(cfme_ip)
    params = {"user_name": cfme_web_ui_user,
        "user_password": cfme_web_ui_password }

    with requests.Session() as sess:
        r = sess.get("{}{}".format(url, "api/auth?requester_type=ui"),
            auth=HTTPBasicAuth(cfme_web_ui_user, cfme_web_ui_password), verify=False,
            allow_redirects=False)
        r = sess.post("{}{}".format(url, "dashboard/authenticate"), params=params, verify=False, allow_redirects=False)
        dump_r(r)
        # Get a protected page now:
        #r = sess.get(url + 'dashboard/show', verify=False, allow_redirects=False)
        for i in range(10):
            r = sess.get("{}{}".format(url, "dashboard/show"), verify=False)
            r = sess.get("{}{}".format(url, "vm_infra/explorer"), verify=False)
            #dump_r(r)
