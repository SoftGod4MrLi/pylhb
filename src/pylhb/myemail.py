"""
模块：myemail
作者：李生
描述：邮件发送
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
import os

class MyEmail:
    """邮件发送类"""
    def __init__(self,fromEmail,fromAuthCode,smtpServer="smtp.qq.com",smtpPort=587) -> None:
        """
        Args:
            fromEmail：发件箱
            fromAuthCode：授权码
            smtpServer：SMTP服务器
            smtpPort：SMTP端口号
        """
        self.fromEmail=fromEmail
        self.fromAuthCode=fromAuthCode
        self.smtpServer=smtpServer
        self.smtpPort=smtpPort
        
    def sendEmail(self,toEmail,subject,content=None,files = None) -> tuple[bool,str]:
        """
        发送邮件
        Args:
            toEmail：收件箱
            subject：主题
            content：内容
            files：附件
        Returns:
            是否成功，执行结果
        """
        try:
            msg = MIMEMultipart()
            # 发件箱
            msg['From'] = self.fromEmail
            # 收件箱
            msg['To'] = toEmail
            # 主题
            msg['Subject'] = Header(subject, 'utf-8').encode()
            # 内容
            if content:
                body = MIMEText(content, "plain", "utf-8")
                msg.attach(body)
            # 附加
            if files:
                for file in files:
                    attachment = open(file, "rb")
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(file)}")
                    msg.attach(part)
            # 发送
            server = smtplib.SMTP(self.smtpServer, self.smtpPort)
            server.starttls()
            server.login(self.fromEmail, self.fromAuthCode)
            server.sendmail(self.fromEmail, toEmail, msg.as_string())
            server.quit()
            return True,"OK"
        except Exception as e:
            return False,f"{e}"