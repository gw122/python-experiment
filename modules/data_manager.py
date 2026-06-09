from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import pandas as pd
import os
from io import BytesIO
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# ==================================================
# 基础配置
# ==================================================
BASE_DIR = os.path.dirname(__file__)

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates")
)

app.secret_key = "data_manage_2026"

# 上传目录
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOW_EXT = {"csv", "xlsx", "xls"}

# ==================================================
# SQLite数据库配置
# ==================================================
DB_PATH = os.path.join(BASE_DIR, "data.db")

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False
)

Base = declarative_base()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ==================================================
# 文件记录表
# ==================================================
class FileRecord(Base):
    __tablename__ = "file_record"

    id = Column(Integer, primary_key=True, autoincrement=True)

    filename = Column(String(200))

    file_path = Column(String(300))


Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ==================================================
# 全局缓存
# ==================================================
global_df = None
global_filename = ""

# ==================================================
# 首页
# ==================================================
@app.route("/", methods=["GET", "POST"])
def index():

    global global_df
    global global_filename

    if request.method == "POST":

        # 检查是否上传文件
        if "file" not in request.files:
            flash("未选择上传文件")
            return redirect(url_for("index"))

        file = request.files["file"]

        if file.filename == "":
            flash("请选择文件")
            return redirect(url_for("index"))

        fname = file.filename

        # 检查后缀
        ext = fname.split(".")[-1].lower()

        if ext not in ALLOW_EXT:
            flash("仅支持 csv、xlsx、xls 文件")
            return redirect(url_for("index"))

        # 保存文件
        save_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            fname
        )

        file.save(save_path)

        # 保存数据库记录
        try:

            new_record = FileRecord(
                filename=fname,
                file_path=save_path
            )

            db.add(new_record)

            db.commit()

        except Exception as e:

            db.rollback()

            print("数据库写入失败：", e)

        # 读取文件
        try:

            if ext == "csv":

                df = pd.read_csv(save_path)

            else:

                df = pd.read_excel(save_path)

            global_df = df

            global_filename = fname

            flash(f"文件 {fname} 上传成功")

        except Exception as e:

            flash(f"文件读取失败：{str(e)}")

        return redirect(url_for("index"))

    # GET请求
    if global_df is not None:

        preview_data = global_df.head(100).to_dict("records")

        cols = global_df.columns.tolist()

        return render_template(
            "index.html",
            data=preview_data,
            columns=cols,
            filename=global_filename
        )

    return render_template(
        "index.html",
        data=None
    )

# ==================================================
# 导出Excel
# ==================================================
@app.route("/export")
def export_file():

    global global_df
    global global_filename

    if global_df is None:

        flash("暂无数据可导出")

        return redirect(url_for("index"))

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        global_df.to_excel(
            writer,
            index=False,
            sheet_name="原始数据"
        )

    output.seek(0)

    file_name = (
        os.path.splitext(global_filename)[0]
        + "_导出.xlsx"
    )

    return send_file(
        BytesIO(output.getvalue()),
        download_name=file_name,
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ==================================================
# 查看上传记录
# ==================================================
@app.route("/file_list")
def get_file_list():

    records = db.query(FileRecord).all()

    return render_template(
        "filelist.html",
        records=records
    )

# ==================================================
# 启动
# ==================================================
if __name__ == "__main__":

    print("数据管理系统启动成功")
    print("访问地址：http://127.0.0.1:5000")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )