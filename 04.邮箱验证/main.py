from flask import *
from func.process import *
app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
def register():
    """
    获取用户名和邮箱信息，写入数据库，并发送请求
    :return:
    """
    if request.method == 'POST':
        # 获取用户名和邮箱
        name = request.form['name']
        email = request.form['email']
        # 写入数据库
        outcome = write_data(name, email)
        if not outcome:
            return redirect(url_for('error'))
        # 发送邮件
        send_email(name, email)
        return redirect(url_for('wait_verified'))
    return render_template('register.html')


@app.route('/error')
def error():
    msg = "Your email have already existed!"
    return render_template('display.html', msg=msg)


@app.route('/fail')
def fail():
    msg = "fail"
    return render_template('display.html', msg=msg)


@app.route('/success')
def success():
    msg = "success"
    return render_template('display.html', msg=msg)


@app.route('/wait_verified')
def wait_verified():
    msg = "The verification link has sent to your email, please check your email"
    return render_template('display.html', msg=msg)


@app.route('/do_verification', methods=['GET'])
def do_verification():
    """
    邮箱验证
    :return:
    """
    token = request.args.get('token')
    authcode = request.args.get('authcode')
    if token and authcode and verify_mail(token, authcode):
        return redirect(url_for('success'))
    else:
        return redirect(url_for('fail'))


if __name__ == '__main__':
    app.run()
