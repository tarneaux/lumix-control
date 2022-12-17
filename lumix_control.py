import requests as r
from urllib import request
import xml.dom.minidom
import http.client
import os
import re

class CameraControl:
    def __init__(self, cam_ip):
        self.cam_ip = cam_ip
        self.baseurl = "http://{ip}/cam.cgi".format(ip=self.cam_ip)
        self.start_camera_control()

    def start_camera_control(self):
        resp = r.get(self.baseurl, params = {"mode": "camcmd", "value": "recmode"})
        if self.check_response(resp):
            print ("Connected")

    def start_stream(self, upd_port):
        resp = r.get(self.baseurl, params = {"mode": "startstream", "value": str(upd_port)})
        resp_2 = r.get(self.baseurl, params = {"mode": "setsetting", "type": "liveviewsize", "value": "vga"})
        resp_3 = r.get(self.baseurl, params = {"mode": "camcmd", "value": "recmode"})
        if self.check_response(resp) and self.check_response(resp_2) and self.check_response(resp_3):
            return True

    def stop_stream(self):
        resp = r.get(self.baseurl, params = {"mode": "stopstream"})
        if self.check_response(resp):
            return True

    def get_state(self):
        resp = r.get(self.baseurl, params = {"mode": "getstate"})
        return resp

    def get_info(self, setting):
        params = {"mode": "getinfo", "type": setting}
        resp = r.get(self.baseurl, params = params )
        return resp

    def current_menu_info(self):
        resp = self.get_info("curmenu")
        return resp

    def all_menu_info(self):
        resp = self.get_info("allmenu")
        return resp

    def get_lens_info(self):
        # ?, max_fstop, min_fstop, max_shutter, min_shutter, ?, ?, max_zoom, min_zoom, ?, ?, ?
        resp = self.get_info("lens")
        return resp

    def get_setting(self, setting):
        params = {"mode": "getsetting", "type": setting}
        resp = r.get(self.baseurl, params = params )
        return resp

    def get_focus_mode(self):
        resp = self.get_setting("focusmode")
        return resp

    def get_focus_mag(self):
        resp = self.get_setting("mf_asst_mag")
        return resp

    def get_mf_asst_setting(self):
        resp = self.get_setting("mf_asst")
        return resp

    def set_setting(self, settings):
        params = {"mode": "setsetting"}
        params.update(settings)
        resp = r.get(self.baseurl, params = params )
        return resp

    def set_iso(self, ISO):
        if ISO == "auto":
            ISO = "50"
        resp = self.set_setting({"type": "iso", "value": ISO})
        if self.check_response(resp):
            print ("ISO set to " + ISO)

    def set_focal(self, focal):
        # 256 between full stops. The rest are third stops.
        # See http://c710720.r20.cf2.rackcdn.com/wp-content/uploads/2011/08/ISO-Shutter-Speeds-Fstops-Copyright-2009-2011-photographyuncapped.gif
        fstop = {
        "1": "0/256",
        "1.1": "85/256",
        "1.2": "171/256",
        "1.4": "256/256",
        "1.6": "341/256",
        "1.8": "427/256",
        "2": "512/256",
        "2.2": "597/256",
        "2.4": "640/256",
        "2.8": "768/256",
        "3.2": "853/256",
        "3.5": "939/256",
        "4" : "1024/256",
        "4.5": "1110/256",
        "5": "1195/256",
        "5.6": "1280/256",
        "6.3": "1364/256",
        "7.1": "1451/256",
        "8": "1536/256",
        "9": "1621/256",
        "10": "1707/256",
        "11": "1792/256",
        "13": "1877/256",
        "14": "1963/256",
        "16": "2048/256",
        "18": "2133/256",
        "20": "2219/256",
        "22": "2304/256"
        }
        resp = self.set_setting({"type": "focal", "value": fstop[focal] })
        if self.check_response(resp):
            print ("F Stop set to " + focal)

    def set_shutter(self, shutter):
        # 256 between full stops. 1 second is the pos/neg boundary
        # See http://c710720.r20.cf2.rackcdn.com/wp-content/uploads/2011/08/ISO-Shutter-Speeds-Fstops-Copyright-2009-2011-photographyuncapped.gif
        shutter_speed = {
        "4000": "3072/256",
        "3200": "2987/256",
        "2500": "2902/256",
        "2000": "2816/256",
        "1600": "2731/256",
        "1300": "2646/256",
        "1000": "2560/256",
        "800": "2475/256",
        "640": "2390/256",
        "500": "2304/256",
        "400": "2219/256",
        "320": "2134/256",
        "250": "2048/256",
        "200": "1963/256",
        "160": "1878/256",
        "125": "1792/256",
        "100": "1707/256",
        "80": "1622/256",
        "60": "1536/256",
        "50": "1451/256",
        "40": "1366/256",
        "30": "1280/256",
        "25": "1195/256",
        "20": "1110/256",
        "15": "1024/256",
        "13": "939/256",
        "10": "854/256",
        "8": "768/256",
        "6": "683/256",
        "5": "598/256",
        "4": "512/256",
        "3.2": "427/256",
        "2.5": "342/256",
        "2": "256/256",
        "1.6": "171/256",
        "1.3": "86/256",
        "1": "0/256",
        "1.3s": "-85/256",
        "1.6s": "-170/256",
        "2s": "-256/256",
        "2.5s": "-341/256",
        "3.2s": "-426/256",
        "4s": "-512/256",
        "5s": "-682/256",
        "6s": "-768/256",
        "8s": "-853/256",
        "10s": "-938/256",
        "13s": "-1024/256",
        "15s": "-1109/256",
        "20s": "-1194/256",
        "25s": "-1280/256",
        "30s": "-1365/256",
        "40s": "-1450/256",
        "50s": "-1536/256",
        "60s": "16384/256",
        "B": "256/256"  
        }
        resp = self.set_setting({"type": "shtrspeed", "value": shutter_speed[shutter] })
        if self.check_response(resp):
            print ("Shutter set to " + shutter)

    def set_video_quality(self, quality="mp4ed_30p_100mbps_4k"):
        # mp4_24p_100mbps_4k / mp4_30p_100mbps_4k
        resp = self.set_setting({"type": "videoquality", "value": quality})
        if self.check_response(resp):
            print ("Video quality set to " + quality)
        return resp

    def focus_control(self, direction="tele", speed="normal"):
        #tele or wide for direction, normal or fast for speed
        params = {"mode": "camctrl", "type": "focus", "value": "{0}-{1}".format(direction, speed)}
        resp = r.get(self.baseurl, params = params )
        return resp

    def rack_focus(self, start_point="current", end_point="0", speed="normal"):
        #tele or wide for direction, normal or fast for speed
        
        #Check where we are with a fine step
        resp = self.focus_control("tele", "normal").text
        current_position = int(resp.split(',')[1])
        
        if end_point == "current":
            end_point = current_position + 13

        # First get to the starting point if necessary
        if start_point == "current":
            start_point = current_position + 13
        elif int(start_point) < current_position:
            while current_position - int(start_point) > 13:
                resp = self.focus_control("tele", "fast").text
                current_position = int(resp.split(',')[1])
        else:
            while int(start_point) - current_position > 13:
                resp = self.focus_control("wide", "fast").text
                current_position = int(resp.split(',')[1])

        #At the start, now let's get to the end point
        start_point = int(start_point)

        threshold = 13
        if speed == "fast":
            threshold = 70

        if start_point > int(end_point):
            while current_position - int(end_point) > threshold:
                resp = self.focus_control("tele", speed).text
                current_position = int(resp.split(',')[1])
                if current_position - int(end_point) <= threshold:
                    #Fine focus for the last bit
                    threshold = 13
                    speed = "normal"
        else:
            while int(end_point) - current_position > threshold:
                resp = self.focus_control("wide", speed).text
                current_position = int(resp.split(',')[1])
                if int(end_point) - current_position <= threshold:
                    threshold = 13
                    speed = "normal"

    def capture_photo(self):
        params = {"mode": "camcmd", "value": "capture"}
        resp = r.get(self.baseurl, params = params)
        return resp

    def video_record_start(self):
        params = {"mode": "camcmd", "value": "video_recstart"}
        resp = r.get(self.baseurl, params = params)
        return resp

    def video_record_stop(self):
        params = {"mode": "camcmd", "value": "video_recstop"}
        resp = r.get(self.baseurl, params = params)
        return resp

    def get_pics(self, dest, do = True, dl = False, regex = ".*"):
        resp = r.get(self.baseurl, params = {"mode": "camcmd", "value": "playmode"})
        resp_num_pics = r.get(self.baseurl, {"mode": "get_content_info"})
        x = xml.dom.minidom.parseString(resp_num_pics.text)
        num_pics = int(x.getElementsByTagName('total_content_number')[0].firstChild.nodeValue)
        print(num_pics)
        page_size = 15
        start = 0
        num_to_download = min(page_size, num_pics-start)
        cam_ip = self.baseurl.split("/")[2]
        print(cam_ip)
        soap_connection = http.client.HTTPConnection(cam_ip, 60606)
        soap_data = '''<?xml version="1.0" encoding="utf-8"?>
            <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
            <s:Body>
            <u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1" xmlns:pana="urn:schemas-panasonic-com:pana">
            <ObjectID>0</ObjectID>
            <BrowseFlag>BrowseDirectChildren</BrowseFlag>
            <Filter>*</Filter>
            <StartingIndex>%d</StartingIndex>
            <RequestedCount>%d</RequestedCount>
            <SortCriteria></SortCriteria>
            <pana:X_FromCP>LumixLink2.0</pana:X_FromCP>
            </u:Browse>
            </s:Body>
            </s:Envelope>
        ''' % (start, num_to_download)
        soap_headers = {
            'Content-Type': 'text/xml; charset="UTF-8"',
            'Content-Length': len(soap_data),
            'SOAPACTION': 'urn:schemas-upnp-org:service:ContentDirectory:1#Browse',
        }
        soap_connection.request('POST', '/Server0/CDS_control', soap_data, soap_headers)
        resp = soap_connection.getresponse()
        x = xml.dom.minidom.parseString(resp.read())
        for res in xml.dom.minidom.parseString(x.getElementsByTagName('Result')[0].firstChild.nodeValue).getElementsByTagName('res'):
            u = res.firstChild.nodeValue
            l = u[u.rindex('/') + 1:]
            if ((l.startswith("DO") and do) or (l.startswith("DL") and dl)):
                if re.match(regex, l):
                    print("downloading ", l)
                    request.urlretrieve(u, os.path.join(dest, l))
                else:
                    print("skipping ", l)

        start += 1

    def check_response(self, resp):
        # Get a 200 response even on error. Have to check <result>
        if "<result>ok</result>" in resp.text:
            return True
        else:
            print (resp.text)
            return False

if __name__ == "__main__":
    IP = "10.0.1.105"
    control = CameraControl(IP) #IP of camera
