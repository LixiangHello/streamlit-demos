import io
import ssl
import base64
import torch
import streamlit as st
import urllib.request
import psutil
from PIL import Image
from process import process

st.set_page_config("Ai抠图(RMBG 2.0)", layout="wide")

st.markdown(
    """<style>
.stDeployButton {
    visibility: hidden;
}
.block-container {
    padding: 3rem 2rem 2rem 2rem;
}
.st-emotion-cache-1mi2ry5 {
    padding: 0rem 1rem;
}
.st-emotion-cache-1gwvy71 {
    padding: 1rem 1rem;
}
</style>""",
    unsafe_allow_html=True,
)

state = st.session_state
if "image" not in state:
    state.image = ""
if "image_nbg" not in state:
    state.image_nbg = ""
if "mask" not in state:
    state.mask = ""
if "filename" not in state:
    state.filename = ""
if "image_stream" not in state:
    state.image_stream = None
if "read_file_once" not in state:
    state.read_file_once = 0


IMAGE_FORMATS = ("jpg", "png", "jpeg", "JPG", "PNG", "JPEG")
DEVICE = "GPU" if torch.cuda.is_available() else "CPU"


@st.dialog("上传图片")
def upload_image(input_image_ph, output_image_ph):

    # 网络图片
    st.markdown("**图片链接**", help="填写网络图片地址")
    cls = st.columns([0.8, 0.2])
    url = cls[0].text_input(
        "xxx", placeholder="url/base64...", label_visibility="collapsed"
    )
    if cls[1].button(
        "读取",
        use_container_width=True,
        # disabled=not url or not url.startswith(("https://", "data:image/")),
    ):
        try:
            if url.startswith(("https://", "http://")):
                content = ssl._create_unverified_context()
                with urllib.request.urlopen(url, context=content) as response:
                    image_data = response.read()
                    state.image_stream = io.BytesIO(image_data)
                    name = "image." + url.rsplit(".", 1)[-1]
            elif url.startswith("data:image/"):
                pfix, base64_data = url.split(",", 1)
                state.image_stream = io.BytesIO(base64.b64decode(base64_data))
                name = "image." + pfix[11:-7]
            else:
                st.warning(":red[请输入有效的图片链接]")
        except Exception as e:
            st.warning(f":red[**读取图片失败，请保存到本地后上传**]")
            return

    # 本地图片
    def _cb():
        state.read_file_once = 1

    st.markdown("**上传图片**")
    file = st.file_uploader(
        "xxx",
        accept_multiple_files=False,
        type=IMAGE_FORMATS,
        label_visibility="collapsed",
        on_change=_cb,
        key="upload_key",
    )
    if state.read_file_once and file:
        state.image_stream = io.BytesIO(file.getvalue())
        name = file.name
        state.read_file_once = 0

    if state.image_stream is not None:
        try:
            image = Image.open(state.image_stream)
            state.image = image
            state.mask = ""
            state.image_nbg = ""
            state.filename = name

            input_image_ph.image(image)
            output_image_ph.empty()
            st.success(":rainbow[**上传成功**]")
        except Exception as e:
            st.warning(f":red[处理图片出错 >> {e}]")

        state.image_stream = None


@st.dialog("下载图片")
def download_image():
    if not state.mask or not state.image_nbg:
        st.warning("请上传图片")
    else:
        with st.spinner("正在处理中..."):
            buffer1 = io.BytesIO()
            state.mask.save(buffer1, format="PNG")
            buffer2 = io.BytesIO()
            state.image_nbg.save(buffer2, format="PNG")

        name = state.filename.rsplit(".", 1)[0] + "-mask.png"
        st.download_button(
            "下载掩码图片",
            data=buffer1.getvalue(),
            file_name=name,
            use_container_width=True,
            disabled=not state.mask,
        )

        name = state.filename.rsplit(".", 1)[0] + "-no-bg.png"
        st.download_button(
            "下载前景图片",
            data=buffer2.getvalue(),
            file_name=name,
            use_container_width=True,
            disabled=not state.image_nbg,
        )


def main():
    st.markdown(
        '<h1 style="text-align: center; color: white; background: #4b4bff; font-size: 26px; border-radius: .5rem; margin-bottom: 15px;">Ai抠图 (RMBG 2.0)</h1>',
        unsafe_allow_html=True,
    )
    body_cls = st.columns(2)

    body_cls[0].markdown(
        "<h6 style='text-align: center;'>原图像</h6>",
        unsafe_allow_html=True,
    )
    body_cls[1].markdown(
        "<h6 style='text-align: center;'>处理后</h6>",
        unsafe_allow_html=True,
    )

    HEIGHT = 400
    input_container = body_cls[0].container(height=HEIGHT)
    output_container = body_cls[1].container(height=HEIGHT)
    input_image_ph = input_container.empty()
    output_image_ph = output_container.empty()

    # show image
    if state.image:
        input_image_ph.image(state.image)
    if state.image_nbg:
        output_image_ph.image(state.image_nbg)

    btm_cls = st.columns(3)
    submit_btn = btm_cls[0].button(
        ":orange[:material/Cloud_Upload: **上传图片**]", use_container_width=True
    )
    process_ph = btm_cls[1].empty()
    process_btn = process_ph.button(
        ":rainbow[:material/Hourglass_Empty: **进行处理**]", use_container_width=True
    )
    download_btn = btm_cls[2].button(
        ":green[:material/Download_2: **下载图片**]",
        use_container_width=True,
        disabled=not state.mask,
    )

    if DEVICE == "CPU":
        cpu_percent = psutil.cpu_percent(interval=0.5)
        cpustates = (
            f"🌟CPU运行会比较慢，请耐心等待一下~🫡(CPU利用率：{cpu_percent:.3f}%)"
        )
        st.caption(
            f'<p style="text-align: center;">{cpustates}</p>',
            unsafe_allow_html=True,
        )

    if submit_btn:
        upload_image(input_image_ph, output_image_ph)

    if process_btn:
        if state.image:
            with output_image_ph.container(), st.spinner(f"正在处理中({DEVICE})..."):
                mask, image_nbg = process(state.image)

            state.image_nbg = image_nbg
            state.mask = mask
            output_container.image(image_nbg)
            st.rerun()
        else:
            st.toast("请上传图片")

    if download_btn:
        download_image()


if __name__ == "__main__":
    main()
