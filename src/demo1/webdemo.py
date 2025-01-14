import joblib
import pandas as pd
import streamlit as st
import streamlit_antd_components as sac

st.set_page_config(
    page_title="梦幻端游用户潜力预测系统",
    page_icon="✨",
    # layout="wide",
    initial_sidebar_state="expanded",
)
state = st.session_state

# 设置样式
st.markdown(
    """<style>
.stDeployButton {
    visibility: hidden;
}
.stMainMenu {
    visibility: hidden;
}
.stAppHeader {
    height: 0rem;
}
.stMainBlockContainer {
    padding: 0rem 6rem 0rem 6rem;
}
.st-emotion-cache-1mi2ry5 {
    padding: 0rem 1rem;
}
.st-emotion-cache-1gwvy71 {
    padding: 1rem 1rem;
}
.class .e1nzilvr5 {
    padding: 0rem 0rem;
}
[data-testid="stDecoration"] {
    background-image: linear-gradient(90deg, rgb(255, 255, 255), rgb(255, 255, 255));
}
[data-testid="stHeader"] {
    height: 0rem;
}
[data-testid="stAppViewBlockContainer"] {
    padding: 0rem 6rem 0rem 6rem;
}

</style>""",
    unsafe_allow_html=True,
)

# [data-testid="stToolbar"] {
#     visibility: hidden;
# }


# 加载模型
@st.cache_resource
def load_model(model_path):

    model = joblib.load(model_path)

    return model


# 预测函数
def predict(model, data):

    df = pd.DataFrame([data])
    prediction = model.predict(df)

    return prediction[0]


# 初始化变量
def init():
    model_path = "model/logistic_regression_model.pkl"
    if "model" not in state:
        state.model = load_model(model_path)
    if "data" not in state:
        state.data = {}
    if "result" not in state:
        state.result = None
    if "running" not in state:
        state.running = False


# 回调函数
def callback_submit():
    state.running = True
    state.data = {
        "梦幻端游_账号_最近30天登录天数": state.d1_key,
        "梦幻端游_账号_近3天浏览不同商品件数": state.d2_key,
        "梦幻端游_角色_玩家30天传音次数": state.d3_key,
        "梦幻端游_角色_空间发布动态数量": state.d4_key,
    }


def body():
    # 页头部
    st.markdown(
        "<h3 style='text-align: center; padding: 0.5rem 0rem 0rem 0rem; '>梦幻端游用户潜力预测系统</h3>",
        unsafe_allow_html=True,
    )
    sac.divider("智能预测", align="center", icon=sac.BsIcon("boxes"))

    st.markdown("")

    # 输入表单
    with st.form("input_form", border=True):
        _colsw = [0.6, 0.3, 0.2]
        _format = (
            lambda x: f'<p style="text-align: right; font-size: 18px; padding: 0.3rem 0 0 0; margin:0; color: black;">{x}<p>'
        )
        cols = st.columns(_colsw)
        cols[0].markdown(_format("最近30天登录天数:"), unsafe_allow_html=True)

        cols[1].number_input(
            "xxx",
            min_value=0,
            value=0,
            step=1,
            label_visibility="collapsed",
            key="d1_key",
        )
        cols = st.columns(_colsw)

        cols[0].markdown(_format("近3天浏览不同商品件数:"), unsafe_allow_html=True)
        cols[1].number_input(
            "xxx",
            min_value=0,
            value=0,
            step=1,
            label_visibility="collapsed",
            key="d2_key",
        )
        cols = st.columns(_colsw)
        cols[0].markdown(_format("玩家30天传音次数:"), unsafe_allow_html=True)
        cols[1].number_input(
            "xxx",
            min_value=0,
            value=0,
            step=1,
            label_visibility="collapsed",
            key="d3_key",
        )
        cols = st.columns(_colsw)
        cols[0].markdown(_format("空间发布动态数量:"), unsafe_allow_html=True)
        cols[1].number_input(
            "xxx",
            min_value=0,
            value=0,
            step=1,
            label_visibility="collapsed",
            key="d4_key",
        )
        st.markdown("")
        st.markdown("")
        cols = st.columns([0.2, 0.6, 0.2])
        cols[1].form_submit_button(
            ":green[**开始预测**]", on_click=callback_submit, use_container_width=True
        )

    st.markdown("")

    # 底部显示
    ph = st.empty()
    if state.running:
        state.running = False
        with ph.container(), st.spinner("正在预测中..."):
            state.result = predict(state.model, state.data)
        # st.toast("**预测完毕~**")

    if state.result is None:
        info = "预测结果：None"
    elif state.result == 1:
        info = f'预测结果💥：<span style="color: green; font-weight: bold; font-size: 30px;">高潜力用户</span>'
    else:
        info = f'预测结果💨：<span style="color: grey; font-weight: bold; font-size: 30px;">低潜力用户</span>'

    ph.markdown(
        f'<p style="text-align: center; font-size: 25px; padding: 0.5rem 0; margin:0; color: black; border: 1.5px dashed grey;">{info}<p>',
        unsafe_allow_html=True,
    )


def main():
    init()
    body()


if __name__ == "__main__":
    main()
