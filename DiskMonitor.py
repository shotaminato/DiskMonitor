import subprocess, smtplib, time, datetime, sys
from email.mime.text import MIMEText
from email.header import Header
sys.path.append("../")
from config_disk_monitor import config


# ../config_disk_monitor/config.py EXAMPLE 
#############################################################
#                                                           #
# MY_EMAIL = "example@gmail.com"                            #
# TO_EMAIL = "to_example@gmail.com"                         #
# MY_PASWORD = "login_passward"                             #
# MY_SMTP_SERVER_NAME = "smtp.gmail.com"                    #
# SSL_PORT = 587                                            #
# CHARSET = "iso-2022-jp"                                   #
# NOTIFICATION_THRESHOLD = 0.15                             #
# INTERVAL_INSECOND = 3600                                  #
#                                                           #
#############################################################

COMMAND = "df | grep /dev/mmcblk"

# メール送信用関数
def send_email(_result,_title): # 文字列,文字列
        # テキストをメール形式に変更（エラー防止も兼ねている）
        _msg = MIMEText(_result, 'plain', config.CHARSET) 
        _msg['Subject'] = Header(_title.encode(config.CHARSET), config.CHARSET)
        smtp_object = smtplib.SMTP(config.MY_SMTP_SERVER_NAME,config.SSL_PORT)
        smtp_object.ehlo()
        smtp_object.starttls()
        smtp_object.login(config.MY_EMAIL,config.MY_PASWORD)
        smtp_object.sendmail(config.MY_EMAIL,config.TO_EMAIL,_msg.as_string())
        smtp_object.quit()

# メイン関数
def main():    
    while 1:

        # 結果の取得
        now = str(datetime.datetime.now()) 
        cp = subprocess.run(COMMAND, capture_output=True, text=True, shell=True)
        rslt_list = cp.stdout.split()
        result =now + "\n"\
                f"  Disc:   {rslt_list[0]}\n"\
                f"  Total:  {rslt_list[1]} KiB\n"\
                f"  Used:   {rslt_list[2]} KiB\n"\
                f"  Avail:  {rslt_list[3]} KiB\n"\
                f"  Use%:   {rslt_list[4]}\n"
        print("\n\n" + result)        

        # 残量チェック。少なければ通知。
        if float(rslt_list[3])/float(rslt_list[1]) < config.NOTIFICATION_THRESHOLD:
            print("Low Storage!!!\n")
            send_email(result,"【要確認】残量が少なくなっています！！")
        
        # 定期的にメッセージ送信
        print("Sending Result...\n")
        send_email(result,"定期通知")

        # 次の送信までのインターバルを設定 [sec]
        time.sleep(config.INTERVAL_INSECOND)


if __name__ == "__main__" :
    main()
