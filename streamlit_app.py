import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# ====================== 全局页面配置 ======================
st.set_page_config(
    page_title="高中生物·光合作用探究实验室",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 解决matplotlib中文乱码
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

# ====================== 标题与课标说明 ======================
st.title("🌿 高中生物｜光合作用多因素探究模拟器")
st.markdown("""
**适配考点**：光照强度、CO₂浓度、光质、**温度**四大影响因素 | 光补偿点/光饱和点/CO₂饱和点 |
温度影响光合酶与呼吸酶活性 | 净光合=总光合-呼吸作用
""")

# ====================== 侧边栏实验控制面板 ======================
with st.sidebar:
    st.header("⚙ 实验变量调控区")
    exp_model = st.radio(
        "🔬 实验探究模式",
        ["自由组合变量", "单一变量：探究光照强度", "单一变量：探究CO₂浓度", 
         "单一变量：探究不同光质", "单一变量：探究环境温度"]
    )
    st.divider()
    
    # 四大实验变量
    light = st.slider("💡 光照强度 (klx)", min_value=0, max_value=120, value=25, step=5)
    co2 = st.slider("🧪 环境CO₂浓度 (μmol/mol)", min_value=0, max_value=120, value=30, step=5)
    temp = st.slider("🌡 环境温度 (℃)", min_value=5, max_value=45, value=25, step=2)
    light_type = st.radio("🎨 入射光质", ["红光", "蓝光", "白光", "绿光"])

# ====================== 生物生理参数定义 ======================
# 1. 光质吸收系数（光合色素吸收光谱）
light_absorb = {
    "红光": 0.98,
    "蓝光": 0.95,
    "白光": 0.80,
    "绿光": 0.12
}

# 2. 温度影响系数（高中标准：植物光合最适25℃，呼吸最适30℃）
def get_temp_photo_factor(t):
    """光合酶活性温度系数"""
    if t < 15:
        return 0.3 + (t-5)*0.03
    elif 15 <= t <= 25:
        return 0.6 + (t-15)*0.04
    elif 25 < t <= 35:
        return 1.0 - (t-25)*0.02
    else:
        return 0.8 - (t-35)*0.08

def get_temp_resp_factor(t):
    """呼吸酶活性温度系数"""
    if t < 15:
        return 0.2 + (t-5)*0.04
    elif 15 <= t <= 30:
        return 0.6 + (t-15)*0.05
    else:
        return 1.3 - (t-30)*0.06

# 基准速率
BASE_RESP = 5.0    # 25℃基准呼吸速率
BASE_PHOTO = 10.0  # 基准总光合基数

# ====================== 核心光合速率计算公式 ======================
def get_net_photosynthesis(light_int, co2_int, opt_color, t):
    # 温度系数
    t_photo_k = get_temp_photo_factor(t)
    t_resp_k = get_temp_resp_factor(t)
    real_resp = round(BASE_RESP * t_resp_k, 2)

    # 光照因子：光补偿点15，光饱和点90
    if light_int <= 0:
        light_factor = 0
    elif 0 < light_int < 15:
        light_factor = light_int * 0.3
    elif 15 <= light_int <= 90:
        light_factor = light_int * 0.8
    else:
        light_factor = 90 * 0.8

    # CO₂因子：CO₂饱和点85
    if co2_int <= 0:
        co2_factor = 0
    elif co2_int <= 85:
        co2_factor = co2_int * 0.75
    else:
        co2_factor = 85 * 0.75

    # 光质系数
    color_k = light_absorb[opt_color]

    # 总光合速率
    total_photo = (light_factor * co2_factor * color_k * t_photo_k) / 60
    net_photo = round(total_photo - real_resp, 2)
    return max(net_photo, -real_resp), real_resp

# 实时计算
net_rate, resp_now = get_net_photosynthesis(light, co2, light_type, temp)

# ====================== 主体页面左右布局 ======================
col_left, col_right = st.columns([1, 1.3])

# 左侧：实时数据+生理状态+知识点
with col_left:
    st.subheader("📊 实时生理指标")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("净光合速率", f"{net_rate} 单位/s")
    with col_m2:
        st.metric("实时呼吸速率", f"{resp_now} 单位/s")
    with col_m3:
        st.metric("环境温度", f"{temp} ℃")

    st.divider()
    st.subheader("🧬 植物生理状态判定")
    if net_rate < 0:
        st.error("🌙 呼吸＞光合：有机物消耗，仅消耗氧气，无气泡释放")
    elif net_rate == 0:
        st.warning("⚖ 补偿点平衡：光合=呼吸，有机物收支持平")
    elif 0 < net_rate < 30:
        st.info("🌤 弱光合积累：少量有机物积累，缓慢释放氧气")
    else:
        st.success("☀ 强光合积累：大量有机物积累，大量释放氧气气泡")

    st.divider()
    st.subheader("📚 对应高中考点")
    if light_type == "绿光":
        st.warning("考点：叶绿素主要吸收红光、蓝紫光，绿光利用率极低")
    elif light >= 90:
        st.success("考点：达到**光饱和点**，光照不再限制光合")
    elif co2 >= 85:
        st.success("考点：达到**CO₂饱和点**，CO₂不再为限制因子")
    if temp < 15:
        st.info("低温抑制酶活性，光合、呼吸速率均偏低")
    elif 23 <= temp <= 27:
        st.success("✅ 最适光合温度区间，净光合效率最高")
    elif temp > 35:
        st.warning("高温抑制光合酶活性，光合快速下降，呼吸仍较强")

# 右侧：水下实景+动态氧气气泡
with col_right:
    st.subheader("🌊 水生植物水下光合实景模拟")
    video_link = "https://static.streamlit.io/examples/flower-demo.mp4"
    st.video(video_link, loop=True, autoplay=True, format="mp4")

    st.subheader("🫧 实时氧气气泡释放动态")
    bubble_count = int(net_rate)
    bubble_style = f"""
    <div style="background:#0088cc;border-radius:15px;padding:20px;height:160px;">
        <h4 style="color:white;margin:0;">水下水草释放O₂气泡</h4>
        <div style="margin-top:15px;font-size:26px;letter-spacing:8px;">
        {"🫧"*bubble_count if bubble_count>0 else "🔴 无氧气释放，仅进行呼吸作用"}
        </div>
    </div>
    """
    st.markdown(bubble_style, unsafe_allow_html=True)

# ====================== 底部：五大类标准探究曲线图 ======================
st.divider()
st.subheader("📈 高中标准光合速率变化曲线图")

def draw_bio_curve(mode):
    fig, ax = plt.subplots(figsize=(10, 5))
    x_list = np.linspace(0, 120, 30)

    if mode == "单一变量：探究光照强度":
        y_list = [get_net_photosynthesis(x, 60, "白光", 25)[0] for x in x_list]
        ax.plot(x_list, y_list, c="#27ae60", lw=2.5, label="净光合速率")
        ax.axhline(y=0, color="red", ls="--", alpha=0.7)
        ax.axvline(x=15, c="orange", ls=":", label="光补偿点")
        ax.axvline(x=90, c="darkgreen", ls=":", label="光饱和点")
        ax.set_xlabel("光照强度(klx)")
        ax.set_ylabel("净光合速率")
        ax.set_title("光照强度对净光合速率影响曲线")

    elif mode == "单一变量：探究CO₂浓度":
        y_list = [get_net_photosynthesis(60, x, "白光", 25)[0] for x in x_list]
        ax.plot(x_list, y_list, c="#2980b9", lw=2.5)
        ax.axvline(x=85, c="red", ls=":", label="CO₂饱和点")
        ax.set_xlabel("CO₂浓度(μmol/mol)")
        ax.set_ylabel("净光合速率")
        ax.set_title("CO₂浓度对净光合速率影响曲线")

    elif mode == "单一变量：探究不同光质":
        color_tags = ["绿光", "白光", "蓝光", "红光"]
        y_vals = [get_net_photosynthesis(60, 60, c, 25)[0] for c in color_tags]
        bar_color = ["#7fff7f","#f0f0f0","#4169e1","#dc143c"]
        ax.bar(color_tags, y_vals, color=bar_color)
        ax.set_ylabel("净光合速率")
        ax.set_title("不同光质下净光合速率对比")

    elif mode == "单一变量：探究环境温度":
        temp_x = np.linspace(5, 45, 30)
        net_y = [get_net_photosynthesis(60,60,"白光",t)[0] for t in temp_x]
        resp_y = [get_net_photosynthesis(60,60,"白光",t)[1] for t in temp_x]
        ax.plot(temp_x, net_y, c="#27ae60", lw=2.5, label="净光合速率")
        ax.plot(temp_x, resp_y, c="#e74c3c", lw=2.5, label="呼吸速率")
        ax.axvline(x=25, c="green", ls="--", alpha=0.6, label="光合最适温")
        ax.axvline(x=30, c="red", ls="--", alpha=0.6, label="呼吸最适温")
        ax.set_xlabel("环境温度(℃)")
        ax.set_ylabel("速率大小")
        ax.set_title("温度对净光合与呼吸速率影响曲线（高考必考）")

    ax.grid(alpha=0.3)
    ax.legend()
    return fig

if exp_model != "自由组合变量":
    pic = draw_bio_curve(exp_model)
    st.pyplot(pic)
else:
    st.info("请在侧边栏选择【单一变量探究模式】，自动生成对应标准曲线图")

# ====================== 实验结论汇总表 ======================
st.divider()
st.subheader("📋 四大因素影响结论（答题直接用）")
conclusion_df = pd.DataFrame({
    "影响因素":["光照强度","CO₂浓度","光质","环境温度"],
    "核心规律":["低于补偿点光合<呼吸；饱和点后不再上升","随浓度升高上升，达饱和点稳定","红光＞蓝光＞白光＞绿光","25℃左右净光合最强，高温光合骤降、呼吸偏高"],
    "农业应用":["适时补光，避免强光灼伤","大棚增有机肥提升CO₂","温室选用红/蓝紫光补光灯","白天适温增产，夜间适当降温抑呼吸"]
})
st.dataframe(conclusion_df, use_container_width=True, hide_index=True)

st.divider()
st.info("💡 高考重难点：昼夜温差大→白天高温促光合，夜晚低温抑呼吸，有机物积累更多！")import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
