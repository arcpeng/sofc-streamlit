import os
import sys
from pathlib import WindowsPath
import numpy as np
from requests.api import head
import streamlit as st
import requests
import pandas as pd
from bokeh.models import ColumnDataSource, Label, LabelSet, Range1d
from bokeh.plotting import figure, output_file, show
import time




# import matplotlib.pyplot as plt

from PIL import Image

def load_image(img):
    im = Image.open(img)
    image = np.array(im)
    return image




#st.set_page_config(page_title=None, page_icon=None, layout='wide', initial_sidebar_state='auto')

API_URL = 'http://178.154.215.108/tote/ivc'


styles_file = open(os.path.join(os.path.dirname(__file__),"style.css"),"r").read()
st.markdown("<style>" + styles_file + "</style>", unsafe_allow_html=True) 



st.sidebar.image(load_image(os.path.join(os.path.dirname(__file__),"Images","logo.png")))





langs = ["ENG","RU"]
col1, col2 = st.sidebar.columns([2,1])
col1.markdown(r"<div style='margin-top:55px;text-align:right;'><hr /></div>", unsafe_allow_html=True)
lang_selected = col2.selectbox("", langs)





works = []

td = {
    "ENG" :[
        [
            'Introduction',
#            'Understanding IVC',
            'Work #1: How SOFC works: Thermodynamics',
            'Work #2: How SOFC works: Ohmic losses',
            'Work #3: How SOFC works: Mass losses',
            'Work #4: From cell to stack',
#            'Futher investigation'
            ],
        'SOFC cloud model',
        'Select the work:',
        'Model parameters',
        'temperature',
        'pressure',
        'electrolyte thickness',
        'conductivity',
        'atm',
        'mA/cm²',
        'S/m',
        'µm',
        'Reset',
        'Run'+u'\u00a0'+'simulation',
        'Allow to refresh',
        'V',
        'mW/cm²',
        'Voltage',
        'Current density',
        'Power',
        "Total consumed H₂, [kg]",
        "Efficiency factor, [%]",
        "Generated power, [kWh]",
        "Generated H₂O, [kg]",
    ],
    "RU" :[
        [
            'Введение',
#            'Understanding IVC',
            'Работа №1: Термодинамика процессов',
            'Работа №2: Омические потери',
            'Работа №3: Концентрационные потери',
            'Работа №4: Калькулятор стека',
#            'Futher investigation'
            ],
        'Модель ТОТЭ',
        'Выбор работы:',
        'Параметры модели',
        'температура',
        'давление',
        'толщина электролита',
        'удельная проводимость',
        'атм',
        'мА/см²',
        'См/м',
        'мкм',
        'Сброс',
        'Запуск'+u'\u00a0'+'симуляции',
        'Обновлять график',
        'В',
        'мВт/см²',
        'Напряжение',
        'Плотность тока',
        'Мощность',
        "Необходимое количество H₂, [кг]",
        "КПД, [%]",
        "Электрическая мощность установки, [кВтч]",
        "Количество H₂O, [кг]",
    ],
}


works = td[lang_selected][0]

st.sidebar.header(td[lang_selected][1])

# tab_selected = st.sidebar.selectbox(td[lang_selected][2], works, index=(st.session_state["work"] if "work" in st.session_state else 0))
# st.session_state["lang"] = lang_selected
# st.session_state["work"] = works.index(tab_selected)

tab_selected = st.sidebar.selectbox(td[lang_selected][2], works)

_temperature, _pressure, _sigma, _ethick, _jm, _H2ac, _H2Oac, _O2cc = 800, 1.1, 2.0, 50, 80, 0.95, 0.05, 0.95




if tab_selected in works[1:4]:
    st.sidebar.subheader(td[lang_selected][3])
    temperature = st.sidebar.slider(
        #'T [temperature], '+u'\N{DEGREE SIGN}'+'K',
        'T [' + td[lang_selected][4] + '], K',
        600, 1000, _temperature, step=10, key="sld_temperature",
    )

    pressure = st.sidebar.slider(
        'p [' + td[lang_selected][5] + '], ' + td[lang_selected][8], 1.0, 3.0, _pressure, step=.1, key="sld_pressure"
    )

    sigma = st.sidebar.slider(
        u'\u03C3'+' [' + td[lang_selected][7] + '], ' + td[lang_selected][10], 0.0, 3.0, _sigma, step=.2, key="sld_sigma"
    )
    ethick = st.sidebar.slider(
        'd [' + td[lang_selected][6] + '], ' + td[lang_selected][11], 15, 155, _ethick, step=5, key="sld_ethick"
    )


    jm = st.sidebar.slider(
        'jₘ , ' + td[lang_selected][9], 10, 150, _jm, step=5, key="sld_jm"
    )

    H2ac = st.sidebar.slider('H₂, %', 0.8, 0.99,
                             _H2ac, step=0.01, key="sld_H2ac")
    H2Oac = st.sidebar.slider(
        'H₂O, %', 0.01, 0.07, _H2Oac, step=0.01, key="sld_H2Oac")


    O2cc = st.sidebar.slider('O₂, %', 0.01, 1.0, _O2cc,
                              step=0.01, key="sld_O2cc")


    for k, v in zip([
        "sld_temperature",
        "sld_pressure",
        "sld_sigma",
        "sld_ethick",
        "sld_jm",
        "sld_H2ac",
        "sld_H2Oac",
        "sld_O2cc"
        ],[_temperature, _pressure, _sigma, _ethick, _jm, _H2ac, _H2Oac, _O2cc]):
        if k not in st.session_state:
            st.session_state[k] = v



    def _update_sliders(temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc):
        st.session_state["sld_temperature"] = temperature
        st.session_state["sld_pressure"] = pressure
        st.session_state["sld_sigma"] = sigma
        st.session_state["sld_ethick"] = ethick
        st.session_state["sld_jm"] = jm
        st.session_state["sld_H2ac"] = H2ac
        st.session_state["sld_H2Oac"] = H2Oac
        st.session_state["sld_O2cc"] = O2cc

    col1, col2, col3 = st.sidebar.columns([1, 2, 1])
    btn_reset = col1.button(td[lang_selected][12], on_click=_update_sliders, kwargs={
                            "temperature": 1000, "pressure": 1.1, "sigma": 2.0, "ethick": 50, "jm": 80, "H2ac": 0.97, "H2Oac": 0.03, "O2cc": 0.95})
    btn_runsimulation = col2.button(td[lang_selected][13])


else:
    temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc = _temperature, _pressure, _sigma, _ethick, _jm, _H2ac, _H2Oac, _O2cc



def get_ivc(temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc):
    payload = {
        "temperature": temperature,
        "pressure": pressure * 101325.0,
        "sigma": sigma,
        "ethick": ethick * pow(10, -6),
        "jm": jm,
        "H2ac": H2ac,
        "H2Oac":H2Oac,
        "O2cc":O2cc
    }
    result = requests.post(API_URL, data=payload).json()
    return {k: np.array(result[k]) for k in result.keys()}






header_container = st.container()
for item in works:
    if tab_selected == item:
        with header_container:
            st.title(item) 
            st.markdown('''
            <hr class="labcontent"/>
            ''', unsafe_allow_html=True)







if tab_selected == works[0] and lang_selected == "RU":

    # st.session_state["work"] = 0

    with st.container():
        st.markdown('''
        <div style="text-align: justify;">
        Современная энергетика базируется в основном на электромеханическом способе преобразования энергии, когда тепловая энергия,
         выделяющаяся при сгорании топлива сначала преобразуется в механическую (обычно вращения), которая в свою очередь 
         преобразуется в электрическую посредством электрогенератора. Однако, обусловленный развитием цивилизации рост 
         энергопотребления при исчерпаемости ископаемых энергоносителей, возрастание их стоимости и близкая к предельной 
         экологическая нагрузка побуждают человечество предпринимать усилия по повышению эффективности преобразования энергии 
         первичных источников в электрическую и развивать альтернативные способы ее производства. Такой альтернативой могут
          стать работающие по принципу прямого преобразования энергии топливные элементы (ТЭ), которые позволяют сразу получать из 
          энергии химических связей топлива электрическую без промежуточного перехода в механическую энергию. Такой процесс 
          получения электроэнергии в ТЭ значительно более эффективен, чем в традиционно используемых в энергетике электромеханических 
          преобразователях. В ТЭ нет движущихся частей что значительно увеличивает КПД процесса.
        <p></p></div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div style="text-align: justify;">
        Нельзя сказать, что ТЭ уже являются обыденными источниками энергии, но несомненно, технологии ТЭ переживают бурное развитие. 
        ТЭ уже находят применение в стационарных энергоустановках широкого диапазона мощностей, транспортных силовых установках, 
        переносных и портативных источниках электропитания.
        <p></p></div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div style="text-align: justify;">
        В ТЭ химическая энергия топлива непосредственно преобразуется в электричество в процессе бесшумной и беспламенной 
        электрохимической реакции. Электролит различных ТЭ может находиться в твёрдом (полимеры, гибридные материалы, керамика)
         или жидком (раствор или расплав) агрегатном состоянии и должен обладать высокой ионной проводимостью (O²⁻, H⁺ 
         и другие ионы, в зависимости от типа ТЭ) в сочетании с пренебрежимо малой электронной проводимостью. Тип электролита 
         часто служит основой при классификации ТЭ.
        <p></p></div>
        ''', unsafe_allow_html=True)


        # <math xmlns="http://www.w3.org/1998/Math/MathML" display="inline-block" title="O^{2-} "> <mrow> <msup> <mrow> O </mrow> <mrow> <mn>2</mn> <mo>-</mo> </mrow> </msup> </mrow></math>
        # <math xmlns="http://www.w3.org/1998/Math/MathML" display="inline-block" title="H^{+} "> <mrow> <msup> <mrow> H </mrow> <mrow> <mo>+</mo> </mrow> </msup> </mrow></math>

        st.markdown('''
        <div style="text-align: justify;">
        Среди различных типов топливных элементов, для энергоустановок стационарного назначения и целого ряда транспортных приложений 
        наиболее подходящими представляются высокотемпературные твердооксидные топливные элементы (ТОТЭ).
        <p></p></div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div style="text-align: justify;">
        ТОТЭ являются топливными элементами с самой высокой рабочей температурой. Рабочая температура ТОТЭ в общем случае может 
        варьироваться от 600°C до 900°C. КПД производства электрической энергии у ТОТЭ – самый высокий из всех топливных элементов и в 
        принципе может достигать 70%.
        <p></p></div>
        ''', unsafe_allow_html=True)


        st.markdown('''
        <div style="text-align: justify;">
        Важнейшими преимуществами ТОТЭ являются широкий спектр потребляемых видов топлива – газообразные и жидкие углеводороды, спирты.
        <p></p></div>
        ''', unsafe_allow_html=True)


        st.markdown('''
        <div style="text-align: justify;">
        Основными компонентами любого единичного ТЭ являются катод, анод и разделяющий их электролит.
        <p></p></div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div style="text-align: justify;">
        Принципиальная рабочая схема любого ТЭ выглядит довольно просто. К одной стороне ТЭ – аноду – необходимо подавать топливо (синтез-газ, 
        содержащий водород и окись углерода, для ТОТЭ; чистый водород для наиболее распространённых низкотемпературных видов ТЭ или 
        другие виды топлив для отдельных типов ТЭ), к другой стороне – катоду – подают воздух (или чистый кислород).
        <p></p></div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div style="text-align: justify;">
        В ТОТЭ анод и катод представляют собой тонкие слои керамических и металлокерамических композитных материалов разного 
        состава с открытой пористостью. Пористая структура электродов необходима, т.к. именно на развитой поверхности 
        многочисленных пор происходят основные химические реакции.
        <p></p></div>
        ''', unsafe_allow_html=True)    

        st.markdown('''
        <div style="text-align: justify;">
        Отличительной особенностью ТОТЭ является то, что для работы при высоких температурах используемый электролит представляет 
        собой тонкую твердую керамическую структуру на основе оксидов металлов, часто в составе содержащих 
        иттрий и цирконий, которая является проводником ионов кислорода (O²⁻). Именно благодаря особенностям электролита 
        твёрдооксидный топливный элемент получил своё название.  
        <p></p></div>
        ''', unsafe_allow_html=True)    

        # <math xmlns="http://www.w3.org/1998/Math/MathML" display="inline-block" title="O^{2-} "> <mrow> <msup> <mrow> O </mrow> <mrow> <mn>2</mn> <mo>-</mo> </mrow> </msup> </mrow></math>

        st.markdown('''
        <div style="text-align: justify;">
        На рисунке 1 показана упрощённая принципиальная схема ТОТЭ.  
        <p></p></div>
        ''', unsafe_allow_html=True) 

        col1, col2, col3 = st.columns([1,6,1])
        col2.image(load_image(os.path.join(os.path.dirname(__file__),"Images","intro_fig1ru.jpg")), width=500, caption="Рисунок 1. − Принципиальная схема ТОТЭ")

        st.markdown('''
        <div style="text-align: justify;">
        Рассмотрим электрохимические реакции в ТОТЭ на простом примере водородного топлива. На катоде протекает реакция восстановления кислорода:
         <p></p></div>
        ''', unsafe_allow_html=True)    

        # <math xmlns="http://www.w3.org/1998/Math/MathML" display="block" title="O_2 + 4\overline{e} = 2O^{2-} "> <mrow> <msub> <mrow> O </mrow> <mrow> <mn>2</mn> </mrow> </msub> <mo>+</mo> <mn>4</mn> <mover accent="true"> <mrow> <mi>e</mi> </mrow> <mo>¯</mo> </mover> <mo>=</mo> <mn>2</mn> <msup> <mrow> O </mrow> <mrow> <mn>2</mn> <mo>-</mo> </mrow> </msup> </mrow>,</math>  


        st.latex(r'''\text{O}_2 + 4\overline{e} = 2\text{O}^{2-}''')

        st.markdown('''
        <div style="text-align: justify;">
        а на аноде – окисления топлива:
        <p></p></div>
        ''', unsafe_allow_html=True)   

        # <math xmlns="http://www.w3.org/1998/Math/MathML" display="block" title="H_2 + O^{2-} = H_2O+ 2\overline{e} "> <mrow> <msub> <mrow> H </mrow> <mrow> <mn>2</mn> </mrow> </msub> <mo>+</mo> <msup> <mrow> O </mrow> <mrow> <mn>2</mn> <mo>-</mo> </mrow> </msup> <mo>=</mo> <msub> <mrow> H </mrow> <mrow> <mn>2</mn> </mrow> </msub> O <mo>+</mo> <mn>2</mn> <mover accent="true"> <mrow> <mi>e</mi> </mrow> <mo>¯</mo> </mover> </mrow></math>  
      

        st.latex(r'''\text{H}_2 + \text{O}^{2-} = \text{H}_2\text{O}+ 2\overline{e} ''')

        st.markdown('''
        <div style="text-align: justify;">
        Ионы кислорода движутся через ионопроводящий твёрдый электролит от катода к аноду, где соединяются с водородом. 
        Продуктом реакции в этом случае является вода. Общая реакция окисления:
        <p></p></div>
        ''', unsafe_allow_html=True)   

        # <math xmlns="http://www.w3.org/1998/Math/MathML" display="block" title="2H_2 + O_2 \rightarrow 2H_2O "> <mrow> <mn>2</mn> <msub> <mrow> H </mrow> <mrow> <mn>2</mn> </mrow> </msub> <mo>+</mo> <msub> <mrow> O </mrow> <mrow> <mn>2</mn> </mrow> </msub> <mo>→</mo> <mn>2</mn> <msub> <mrow> H </mrow> <mrow> <mn>2</mn> </mrow> </msub> O </mrow>,</math>
 

        st.latex(r'''2\text{H}_2 + \text{O}_2 \rightarrow 2\text{H}_2\text{O}''')

        st.markdown('''
        <div style="text-align: justify;">
        такая же, как и при горении водорода. Однако в ТЭ потоки топлива и окислителя не смешиваются, а реакции окисления топлива 
        и восстановления кислорода, как и в батарейках, пространственно разделены и проходят на разных электродах – соответственно, 
        процесс «сжигания» протекает, только если элемент попутно выдает ток во внешнюю цепь, вырабатывая электричество.  
        <p></p></div>
        ''', unsafe_allow_html=True)   


        # <math xmlns="http://www.w3.org/1998/Math/MathML" display="inline-block" title="O^{2-} "> <mrow> <msup> <mrow> O </mrow> <mrow> <mn>2</mn> <mo>-</mo> </mrow> </msup> </mrow></math>
        st.markdown('''
        <div style="text-align: justify;">
        Электролит ТОТЭ обеспечивает транспорт ионов кислорода O²⁻ от катода к аноду и разделяет два газовых объёма: 
        топливный и окислительный. Высоко избирательные ионопроводящие свойства твёрдого электролита (при минимально 
        возможной электронной проводимости) достигаются тщательным подбором состава (соотношения основных компонентов 
        и легирующих добавок) и специальными методами изготовления из него прецизионных тонкоплёночных структур, 
        обеспечивающих газовую непроницаемость и высокую ионную проводимость. Ионопроводящая эффективность электролита 
        напрямую зависит от толщины и температуры – падает с ростом первой и растёт с ростом второй. Чем тоньше можно 
        сделать плёнку электролита, тем лучшую ионную проводимость он обеспечивает. При этом очень высокая температура 
        процесса в ТОТЭ помимо преимущества в виде высокой эффективности имеет и существенные недостатки, а именно, 
        необходимость применения в ТОТЭ дорогостоящих материалов, способных выдерживать такие критические условия на 
        протяжении длительного времени. Уменьшая толщину электролита, можно в некоторой степени снизить температуру 
        процесса в ТОТЭ, что очень важно с точки зрения подбора более доступных и дешёвых материалов для ТОТЭ.  
        <p></p></div>
        ''', unsafe_allow_html=True)   

        st.markdown('''
        <div style="text-align: justify;">
        Не менее важным является подбор эффективных материалов для катода и анода, т.к. они должны отвечать целому 
        комплексу специфических, часто противоречивых требований: химическая стойкость и стабильность при высоких 
        температурах в условиях характерных рабочих сред, высокая проницаемость для прохождения рабочих газовых сред 
        при достаточной прочности, хорошая адгезия и взаимная совместимость по коэффициенту термического расширения с 
        материалом электролита в широком диапазоне температур, определённые каталитические свойства анодного материала, 
        интенсифицирующие проведение целевой электрохимической реакции.
        <p></p></div>
        ''', unsafe_allow_html=True)   

        st.markdown('''
        <div style="text-align: justify;">
        Следует отметить для представления сложностей в производстве, что толщина электролита, в зависимости от 
        подхода производителей, варьируется примерно от 10 до 150 микрон, то есть от 0.01 до 0.15 мм. Толщины анода 
        и катода имеют схожий порядок величин.
        <p></p></div>
        ''', unsafe_allow_html=True)  

        st.markdown('''
        <div style="text-align: justify;">
        Батареи топливных элементов, которые находят непосредственное применение в электрохимических генераторах, 
        состоят из определённого количества собранных совместно единичных ТЭ (трубок) и других вспомогательных элементов, 
        позволяющих работать отдельным ТЭ совместно, обеспечивающих равномерную подачу топлива и окислителя к анодам и 
        катодам всех ТЭ одновременно, вывод отработанных продуктов реакции и электрическую коммутацию, внутреннюю и внешнюю.
        <p></p></div>
        ''', unsafe_allow_html=True)  

        st.markdown('''
        <div style="text-align: justify;">
        Рисунок 2 представляет примерное устройство условного единичного блока планарного ТОТЭ, с организацией подвода 
        топлива и окислителя к рабочим поверхностям электродов.
        <p></p></div>
        ''', unsafe_allow_html=True)  

        col1, col2, col3 = st.columns([1,6,1])
        col2.image(load_image(os.path.join(os.path.dirname(__file__),"Images","intro_fig2ru.jpg")), width=500, caption="Рисунок 2. − Пример устройства единичного планарного ТОТЭ")


        st.markdown('''
        <div style="text-align: justify;">
        Если изображённую на рисунке 2 единичную структуру многократно повторить при последовательном 
        её сложении по оси Y, получится батарея планарных топливных элементов, как показано на рисунке 3.
        <p></p></div>
        ''', unsafe_allow_html=True)  

        col1, col2, col3 = st.columns([1,6,1])
        col2.image(load_image(os.path.join(os.path.dirname(__file__),"Images","intro_fig3ru.jpg")), width=500, caption="Рисунок 3. − Пример формирования планарной батареи ТОТЭ")


        st.markdown('''
        <div style="text-align: justify;">
        Батарея трубчатых ТОТЭ представляет собой общий коллектор из множества параллельных трубок, внутренняя полость которых предназначена для движения одной 
        из рабочих сред (топлива или окислителя), а наружное пространство – для другой, как в упрощённом виде показано на рисунке 4.
        <p></p></div>
        ''', unsafe_allow_html=True)  

        col1, col2, col3 = st.columns([1,6,1])
        col2.image(load_image(os.path.join(os.path.dirname(__file__),"Images","intro_fig4ru.jpg")), width=500, caption="Рисунок 4. − Пример организации батареи трубчатых ТОТЭ")



if tab_selected == works[0] and lang_selected == "ENG":

    # st.session_state["work"] = 0

    cflag = False

    if cflag:

        st.markdown('''
        Under construction...
        ''')
    else:

        with st.container():
            st.markdown('''
            <div style="text-align: justify;">
            Modern power engineering is based mainly on the electromechanical energy conversion, when the thermal energy 
            eleased from the combustion of fuel is first converted into mechanical (usually rotation) energy, which in 
            turn is converted into electrical energy by means of an electric generator. However, the growth in energy 
            consumption with energy carriers exhaustion, their cost increase, and the environmental burden close to the 
            limit encourage humanity to make efforts to improve the efficiency of converting primary energy sources into 
            electrical energy and to develop alternative methods of its production. Such an alternative can be fuel cells (FC)
            operating on the principle of direct energy conversion, which allow you to immediately obtain electrical energy 
            from the energy of chemical bonds of fuel without an intermediate conversion into mechanical energy. 
            This process of generating electricity is much more efficient than traditional ones. There are no moving parts 
            in a fuel cell, which significantly increases the efficiency of the process.
            <p></p></div>
            ''', unsafe_allow_html=True)

            st.markdown('''
            <div style="text-align: justify;">
            It cannot be said that fuel cells are already usual sources of energy, but undoubtedly, 
            fuel cell technologies are undergoing rapid development. Fuel cells are already being used in stationary 
            power plants of a wide range of capacities, energy systems of vehicles and portable power sources.
            <p></p></div>
            ''', unsafe_allow_html=True)

            st.markdown('''
            <div style="text-align: justify;">
            In a fuel cell, the chemical energy of the fuel is directly converted into electricity in the process of a 
            silent and flame-free electrochemical reaction. The electrolyte of various fuel cells can be in a solid 
            (polymers, hybrid materials, ceramics) or liquid (solution or melt) aggregate state and must have high ionic 
            conductivity (O²⁻, H⁺ and other ions, depending on the type of fuel cell) in combination with a negligible electronic
            conductivity. The type of electrolyte often serves as the basis for the classification of fuel cells.
            <p></p></div>
            ''', unsafe_allow_html=True)


            # <math xmlns="http://www.w3.org/1998/Math/MathML" display="inline-block" title="O^{2-} "> <mrow> <msup> <mrow> O </mrow> <mrow> <mn>2</mn> <mo>-</mo> </mrow> </msup> </mrow></math>
            # <math xmlns="http://www.w3.org/1998/Math/MathML" display="inline-block" title="H^{+} "> <mrow> <msup> <mrow> H </mrow> <mrow> <mo>+</mo> </mrow> </msup> </mrow></math>

            st.markdown('''
            <div style="text-align: justify;">
            Among the various types of fuel cells for stationary power plants and a variety of transport applications, 
            high-temperature solid oxide fuel cells (SOFC) seem to be the most suitable
            <p></p></div>
            ''', unsafe_allow_html=True)

            st.markdown('''
            <div style="text-align: justify;">
            SOFC are the fuel cells with the highest operating temperature. In general, the operating temperature of the SOFC can vary from 600°C to 900°C. 
            The efficiency of electric energy production in SOFC is the highest of all fuel cells and can reach 70%.
            <p></p></div>
            ''', unsafe_allow_html=True)


            st.markdown('''
            <div style="text-align: justify;">
            The most important advantage of SOFC is the possibility of using a wide range of fuels – gaseous and liquid hydrocarbons, alcohols.
            <p></p></div>
            ''', unsafe_allow_html=True)


            st.markdown('''
            <div style="text-align: justify;">
            The main components of any single FC are the cathode, the anode, which are separated by the electrolyte.
            <p></p></div>
            ''', unsafe_allow_html=True)

            st.markdown('''
            <div style="text-align: justify;">
            The basic working scheme of any FC looks quite simple. To one side of the FC – the anode – it is necessary to supply fuel 
            (synthesis gas containing hydrogen and carbon monoxide for SOFC; pure hydrogen for the most common low-temperature 
            types of FC or other fuels for certain types of FC), to the other side – the cathode – it is necessary to supply air (or pure oxygen).
            <p></p></div>
            ''', unsafe_allow_html=True)

            st.markdown('''
            <div style="text-align: justify;">
            In a FC, the anode and cathode are thin layers of ceramic and metal-ceramic composite materials of different compositions with open porosity. 
            The porous structure of the electrodes is necessary, because the main chemical reactions occur it on the developed surface of numerous pores.
            <p></p></div>
            ''', unsafe_allow_html=True)    

            st.markdown('''
            <div style="text-align: justify;">
            A distinctive feature of the SOFC is that for operation at high temperatures, the electrolyte is a thin solid ceramic structure based on metal oxides, often containing 
            yttrium and zirconium, which is a conductor of oxygen ions (O²⁻). It is thanks to the features of the electrolyte that the solid oxide fuel cell got its name.
            <p></p></div>
            ''', unsafe_allow_html=True)    

            # <math xmlns="http://www.w3.org/1998/Math/MathML" display="inline-block" title="O^{2-} "> <mrow> <msup> <mrow> O </mrow> <mrow> <mn>2</mn> <mo>-</mo> </mrow> </msup> </mrow></math>

            st.markdown('''
            <div style="text-align: justify;">
            Figure 1 shows a simplified schematic diagram of the SOFC.  
            <p></p></div>
            ''', unsafe_allow_html=True) 

            col1, col2, col3 = st.columns([1,6,1])
            col2.image(load_image(os.path.join(os.path.dirname(__file__),"Images","intro_fig1eng.jpg")), width=500, caption="Figure 1. − A schematic diagram of a SOFC")

            st.markdown('''
            <div style="text-align: justify;">
            Let's consider electrochemical reactions in SOFC on a simple example of hydrogen fuel. An oxygen reduction reaction takes place at the cathode:
            <p></p></div>
            ''', unsafe_allow_html=True)    

            # <math xmlns="http://www.w3.org/1998/Math/MathML" display="block" title="O_2 + 4\overline{e} = 2O^{2-} "> <mrow> <msub> <mrow> O </mrow> <mrow> <mn>2</mn> </mrow> </msub> <mo>+</mo> <mn>4</mn> <mover accent="true"> <mrow> <mi>e</mi> </mrow> <mo>¯</mo> </mover> <mo>=</mo> <mn>2</mn> <msup> <mrow> O </mrow> <mrow> <mn>2</mn> <mo>-</mo> </mrow> </msup> </mrow>,</math>  


            st.latex(r'''\text{O}_2 + 4\overline{e} = 2\text{O}^{2-}''')

            st.markdown('''
            <div style="text-align: justify;">
            and the fuel is oxidized at the anode:
            <p></p></div>
            ''', unsafe_allow_html=True)   

            # <math xmlns="http://www.w3.org/1998/Math/MathML" display="block" title="H_2 + O^{2-} = H_2O+ 2\overline{e} "> <mrow> <msub> <mrow> H </mrow> <mrow> <mn>2</mn> </mrow> </msub> <mo>+</mo> <msup> <mrow> O </mrow> <mrow> <mn>2</mn> <mo>-</mo> </mrow> </msup> <mo>=</mo> <msub> <mrow> H </mrow> <mrow> <mn>2</mn> </mrow> </msub> O <mo>+</mo> <mn>2</mn> <mover accent="true"> <mrow> <mi>e</mi> </mrow> <mo>¯</mo> </mover> </mrow></math>  
        

            st.latex(r'''\text{H}_2 + \text{O}^{2-} = \text{H}_2\text{O}+ 2\overline{e} ''')

            st.markdown('''
            <div style="text-align: justify;">
            Oxygen ions move through the ion-conducting solid electrolyte from the cathode to the anode, 
            where they combine with hydrogen. The reaction product in this case is water. The general oxidation reaction:
            <p></p></div>
            ''', unsafe_allow_html=True)   

            # <math xmlns="http://www.w3.org/1998/Math/MathML" display="block" title="2H_2 + O_2 \rightarrow 2H_2O "> <mrow> <mn>2</mn> <msub> <mrow> H </mrow> <mrow> <mn>2</mn> </mrow> </msub> <mo>+</mo> <msub> <mrow> O </mrow> <mrow> <mn>2</mn> </mrow> </msub> <mo>→</mo> <mn>2</mn> <msub> <mrow> H </mrow> <mrow> <mn>2</mn> </mrow> </msub> O </mrow>,</math>
    

            st.latex(r'''2\text{H}_2 + \text{O}_2 \rightarrow 2\text{H}_2\text{O}''')

            st.markdown('''
            <div style="text-align: justify;">
            is the same as in the hydrogen burning. However, in a fuel cell, the flows of fuel and oxidizer don't mix, 
            and the reactions of fuel oxidation and oxygen reduction, as in batteries, are spatially separated and take place 
            on different electrodes, respectively, the «burning» process proceeds only if the element simultaneously generates 
            current to the external circuit, producing electricity.  
            <p></p></div>
            ''', unsafe_allow_html=True)   


            # <math xmlns="http://www.w3.org/1998/Math/MathML" display="inline-block" title="O^{2-} "> <mrow> <msup> <mrow> O </mrow> <mrow> <mn>2</mn> <mo>-</mo> </mrow> </msup> </mrow></math>
            st.markdown('''
            <div style="text-align: justify;">
            The electrolyte of the fuel cell provides transport of oxygen ions O²⁻ from the cathode to the anode and separates two gas volumes: 
            fuel and oxidative. Highly selective ion-conducting properties of a solid electrolyte (with the lowest possible electronic conductivity) 
            are achieved by careful selection of the composition (the ratio of the main components and alloying additives) and special methods of 
            production of precision thin-film structures from it, providing gas impermeability and high ionic conductivity. The ion-conducting efficiency 
            of the electrolyte directly depends on the thickness and temperature – it decreases with the growth of the first and increases with the growth 
            of the second. The thinner the electrolyte film, the better the ionic conductivity. At the same time, the very high temperature of the process 
            in the SOFC, in addition to the advantages in the form of high efficiency, has significant disadvantages, namely, the need to use expensive
            materials in the SOFC that can withstand such critical conditions for a long time. By reducing the thickness of the electrolyte it’s 
            possible to reduce the temperature of the process, which is very important from the point of view of selecting more affordable and cheaper
            materials for the SOFC.  
            <p></p></div>
            ''', unsafe_allow_html=True)   

            st.markdown('''
            <div style="text-align: justify;">
            Equally important is the selection of effective materials for the cathode and the anode, because they must meet a whole set of
            specific, often contradictory requirements: chemical resistance and stability at high temperatures in typical working environments, 
            high permeability for the passage of working gas environment with sufficient strength, good adhesion and mutual compatibility 
            in terms of thermal expansion coefficient with the electrolyte material in a wide temperature range, certain catalytic properties 
            of the anode material, intensifying the main electrochemical reaction.
            <p></p></div>
            ''', unsafe_allow_html=True)   

            st.markdown('''
            <div style="text-align: justify;">
            It should be noted to represent the difficulties in production that the thickness of the electrolyte, depending on 
            the approach of manufacturers, varies from about 10 to 150 microns, that is, from 0.01 to 0.15 mm. The thicknesses of 
            the anode and the cathode have a similar order of value.
            <p></p></div>
            ''', unsafe_allow_html=True)  

            st.markdown('''
            <div style="text-align: justify;">
            Fuel cell batteries, which are directly used in electrochemical generators, consist of a certain number of 
            single FC assembled together and other auxiliary elements that allow individual fuel cells to work together 
            and ensure uniform supply of fuel and oxidizer to the anodes and the cathodes of all fuel cells simultaneously, 
            the output of spent reaction products and internal and external electrical switching.
            <p></p></div>
            ''', unsafe_allow_html=True)  

            st.markdown('''
            <div style="text-align: justify;">
            Figure 2 shows an approximate organization of a conditional single unit of a planar SOFC with the organization 
            of fuel and oxidizer supply to the working surfaces of the electrodes.
            <p></p></div>
            ''', unsafe_allow_html=True)  

            col1, col2, col3 = st.columns([1,6,1])
            col2.image(load_image(os.path.join(os.path.dirname(__file__),"Images","intro_fig2eng.jpg")), width=500, caption="Figure 2. − An approximate organization of a conditional single unit of a planar SOFC")


            st.markdown('''
            <div style="text-align: justify;">
            If the single structure shown in Figure 2 is repeated many times with its sequential addition along the y axis, 
            a fuel cell battery will be obtained, as shown in Figure 3.
            <p></p></div>
            ''', unsafe_allow_html=True)  

            col1, col2, col3 = st.columns([1,6,1])
            col2.image(load_image(os.path.join(os.path.dirname(__file__),"Images","intro_fig3eng.jpg")), width=500, caption="Figure 3. − An example of the formation of a planar SOFC battery")


            st.markdown('''
            <div style="text-align: justify;">
            A tubular SOFC battery is a common collector of many parallel tubes, the inner cavity of which is designed for the movement of one 
            of the working environments (fuel or oxidizer), and the outer space is designed for the other, as shown in simplified form in Figure 4.
            <p></p></div>
            ''', unsafe_allow_html=True)  

            col1, col2, col3 = st.columns([1,6,1])
            col2.image(load_image(os.path.join(os.path.dirname(__file__),"Images","intro_fig4eng.jpg")), width=500, caption="Figure 4. − An example of the organization of a tubular SOFC battery")







# @st.cache(allow_output_mutation=True)
class VI():
    def __init__(self,id=None) -> None:
        self.id = id

    @st.cache(allow_output_mutation=True)
    def makePlotVI(self,params=None):
        temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc = params
        _result = get_ivc(temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc)
        # time.sleep(3)
        _p = figure(
            x_axis_label=td[lang_selected][18] + ', ' + td[lang_selected][9],
            y_axis_label=td[lang_selected][17] + ', '+ td[lang_selected][15],
            plot_width=500, plot_height=300,
        )
        _p.sizing_mode = "scale_both"
        _p.line(_result['i'], (_result['Eload']-_result['eta_con']),  line_width=2)
        _p.axis.axis_label_text_font_style = 'bold'
        # _p.add_layout(_text)
        return _p


class PI():

    def __init__(self,id=None) -> None:
        self.id = id
    
    @st.cache(allow_output_mutation=True)
    def makePlotPI(self,params=None):
        temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc = params
        _result = get_ivc(temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc)
        # time.sleep(3)
        _p = figure(
            x_axis_label=td[lang_selected][18] + ', ' + td[lang_selected][9],
            y_axis_label=td[lang_selected][19] + ', '+ td[lang_selected][16],
            plot_width=500, plot_height=300,
        )
        _p.sizing_mode = "scale_both"
        _p.line(_result['i'], _result['i'] * (_result['Eload']-_result['eta_con']),  line_width=2)
        _p.axis.axis_label_text_font_style = 'bold'
        # _p.add_layout(_text)
        return _p


for k in ["vi1","vi2","vi3","vi4","vi5","vi6","vi7","vi8","pi1","pi2"]:
    if k not in st.session_state.keys():
        st.session_state[k] = [
            temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc]




task_title = lambda tsk,ttl: '''
    <div style="text-align: center; padding:70px 0px 10px 0px"> 
    <span style="padding:2px 7px 2px 7px;color:white;background-color: rgb(77,77,77);border-radius:3px;display:inline-flex;justify-content:center;align-items:center;font-weight:bold;">{0:s}</span><span style="padding-left:10px;">{1:s}</span>
    <p></p></div>
    '''.format(tsk,ttl)

task_subtitle = lambda ttl: '''
    <div style="text-align: center;font-weight:bold; padding:30px 0px 10px 0px""> 
    {0:s}
    <p></p></div>
    '''.format(ttl)

plt_statetitle = lambda sts: '''
        <div style="text-align: right;font-size: 12px; padding-top:2px;">        
        <b>Saved state:</b> {0:.0f} K, {1:.1f} atm, {2:.2f}⋅10⁻⁶ S/m, {3:.2f} µm, {4:.2f} mA/cm²
        <p></p></div>
        '''.format(*st.session_state[sts])



plt_vi1 = VI("vi1")
plt_vi2 = VI("vi2")
plt_vi3 = VI("vi3")
plt_vi4 = VI("vi4")
plt_vi5 = VI("vi5")
plt_vi6 = VI("vi6")
plt_vi7 = VI("vi7")
plt_vi8 = VI("vi8")
plt_pi1 = PI("pi1")
plt_pi2 = PI("pi2")



if tab_selected == works[1] and lang_selected == "RU":

    # st.session_state["work"] = 1

    with st.container():
        st.header("Влияние температуры на характеристики топливного элемента")
        st.markdown('''
        <div style="text-align: justify;">  
        Эффективность топливного элемента зависит от электрохимических реакций, протекающих в нём между топливом (водородом) и кислородом. Так, в стандартных или нормальных условиях (температура 25 °C, давление 1 атм, постоянные, равные 1, эффективные концентрации (активности) компонентов), "идеальный" топливный элемент будет выдавать т.н. стандартное напряжение (E<sub>0</sub>), значение которого определяется конкретным типом реакциии и участвующими реагентами. Однако, топливные элементы часто эксплуатируются в условиях, значительно отличающихся от стандартных. Например, высокотемпературные топливные элементы работают при температуре 700–1000 °C, автомобильные топливные элементы часто работают при давлениях 3–5 атм, и почти все во всех этих случаях имеет место изменение концентрации (и, следовательно, активностей) реагентов.  В данной работе мы определим, как именно отклонения от стандартных условий влияют на значение напряжения топливного элемента: сначала изучим влияние температуры, а затем давления.
        <p></p></div>
        ''', unsafe_allow_html=True)


       
        with st.container():  
            
            st.markdown('''
            Чтобы понять, как меняется напряжение топливного элемента в зависимости от температуры, рассмотрим выражение для свободной энергии Гиббса (G) в дифференциальной форме – одно из важнейших термодинамических соотношений для описания протекающих в топливном элементе химических реакций:
            ''')

            st.latex(r'''
            \tag{1} dG = −SdT + Vdp
            ''')

            st.markdown(''' 
            где S это энтропия, T, V и p  - термодинамические параметры системы (температура, объём и давление соответственно).  

            В нормировке на один моль вещества, выражение (1) можно записать в виде:
            ''')

            st.latex(r'''
            \tag{2} \left(\frac{d (\Delta g)}{dT}
            \right)_p = −\Delta s
            ''')

            st.markdown('''
            Свободную энергию Гиббса Δg можно выразить через напряжение топливного элемента E, константу Фарадея F и количество переносимых 
            электронов n следующим образом:
            ''')

            st.latex(r'''
            \tag{3} \Delta g = -nFE
            ''')   

            st.markdown('''
            Объединив уравнения (2) и (3), найдем выражение для напряжения E топливного элемента как функции температуры:
            ''')         

            st.latex(r'''
            \tag{4} \left(\frac{dE}{dT}\right)_p = \frac{\Delta s}{nF}
            ''')   


            st.markdown('''
            или в интегральной форме:
            ''')

            st.latex(r'''
            \tag{5} E_T=E_0+ nF \cdot \Delta s \cdot (T−T_0) 
            ''')   

            st.markdown('''
            где E<sub>T</sub> – напряжение топливного элемента при произвольной температуре T и постоянном давлении. 
            Как правило, предполагается, что Δs не зависит от температуры, однако если значение E<sub>T</sub> требуется рассчитать более точно, 
            это можно сделать путём интегрирования выражения для Δs как функции температуры.
            ''', unsafe_allow_html=True)

            st.markdown('''
            Приведённое ниже задание поможет Вам понять влияние рабочей температуры топливного элемента на его напряжение.
            ''')


            st.markdown(task_title("Задание 1.1","Области низких и высоких температур"), unsafe_allow_html=True)

            st.markdown(task_subtitle("Работа с моделью"), unsafe_allow_html=True)

            st.markdown('''
            * На боковой панели  `Параметры модели` установите температуру T на 700 К.
            * Установите флажок `Обновлять график` над графиком ниже и нажмите на кнопку `Запуск симуляции` внизу боковой панели.
            * График обновится. Снимите флажок с функции `Обновлять график`, чтобы зафиксировать полученные результаты.
            ''')




        
            col1, col2 = st.columns([2,1])
            chk_vi1 = col2.checkbox(td[lang_selected][14], key="chk_vi1")
            if chk_vi1 and btn_runsimulation:
                st.session_state["vi1"] = [
                    temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc]
            st.bokeh_chart(plt_vi1.makePlotVI(st.session_state["vi1"]))
            col1.markdown(plt_statetitle("vi1"), unsafe_allow_html=True)


            st.markdown('''
            * На боковой панели  `Параметры модели` установите температуру T на 900 К.
            * Установите флажок `Обновлять график` над графиком ниже и нажмите на кнопку `Запуск симуляции` внизу боковой панели.
            * График обновится. Снимите флажок с функции `Обновлять график`, чтобы зафиксировать полученные результаты.
            ''')


            col1, col2 = st.columns([2,1])
            chk_vi2 = col2.checkbox(td[lang_selected][14], key="chk_vi2")
            if chk_vi2 and btn_runsimulation:
                st.session_state["vi2"] = [
                    temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc]

            st.bokeh_chart(plt_vi2.makePlotVI(st.session_state["vi2"]))
            col1.markdown(plt_statetitle("vi2"), unsafe_allow_html=True)

            st.markdown(task_subtitle("Анализ результатов"), unsafe_allow_html=True)


            st.markdown(r'''
            Сравните полученные графики и ответьте на следующие вопросы:
            <ol class="rectangle-list">
            <li>Как напряжение топливного элемента V меняется с изменением температуры T?</li>
            <li>Как Ваши предположения соотносятся с приведённым выше выражением (5)?</li>
            </ol>
            ''', unsafe_allow_html=True)


        with st.container():

            st.header("Влияние давления на характеристики топливного элемента")

            st.markdown('''
            Как и температурный эффект, влияние давления на напряжение топливного элемента может быть получено из полного дифференциала
            свободной энергии Гиббса (1) и его электрохимического выражения (3):
            ''', unsafe_allow_html=True)

            st.latex(r'''
            \left(\frac{dG}{dp}\right)_T = \Delta V \Rightarrow \left(\frac{d (\Delta g)}{dp}\right)_T = \Delta v 
            ''')

            st.markdown('''
            И чего следует, что:
            ''')

            st.latex(r'''
            \tag{6} \left(\frac{dE}{dp}\right)_T = -\frac{\Delta v}{nF} 
            ''')

            st.markdown('''
            Выражение (6) показывает, что изменение напряжение топливного элемента связано с изменением объёма реагентов. 
            Если изменение объёма отрицательно, то есть в результате реакции образуется меньше молей газа, чем вступило в реакцию, 
            напряжение топливного элемента будет увеличиваться с увеличением давления. Этот вывод соответствует *принципу Ле Шателье*: 
            если на систему, находящуюся в устойчивом равновесии, воздействовать извне, изменяя какое-либо из условий равновесия 
            (температуру, давление, концентрацию, внешнее электромагнитное поле), то в системе усиливаются процессы, направленные в 
            сторону противодействия изменениям.
            ''')

            st.markdown('''
            Понять, как работает топливный элемент при давлении, отличающемся от стандартного, вам поможет следующее задание.
            ''')


            st.markdown(task_title("Задание 1.2","Области нормального и высокого давлений"), unsafe_allow_html=True)

            st.markdown(task_subtitle("Работа с моделью"), unsafe_allow_html=True)

            st.markdown('''
            * На боковой панели  `Параметры модели` установите давление p равным 1.1 атм.
            * Установите флажок `Обновлять график` над графиком ниже и нажмите на кнопку `Запуск симуляции` внизу боковой панели.
            * График обновится. Снимите флажок с функции `Обновлять график`, чтобы зафиксировать полученные результаты.
            ''')

        
            col1, col2 = st.columns([2,1])
            chk_vi3 = col2.checkbox(td[lang_selected][14], key="chk_vi3")
            if chk_vi3 and btn_runsimulation:
                st.session_state["vi3"] = [
                    temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc]
            st.bokeh_chart(plt_vi3.makePlotVI(st.session_state["vi3"]))
            col1.markdown(plt_statetitle("vi3"), unsafe_allow_html=True)
    

            st.markdown('''
            * На боковой панели  `Параметры модели` увеличьте давление до 1.8 атм.
            * Установите флажок `Обновлять график` над графиком ниже и нажмите на кнопку `Запуск симуляции` внизу боковой панели.
            * График обновится. Снимите флажок с функции `Обновлять график`, чтобы зафиксировать полученные результаты.
            ''')

        
            col1, col2 = st.columns([2,1])
            chk_vi4 = col2.checkbox(td[lang_selected][14], key="chk_vi4")
            if chk_vi4 and btn_runsimulation:
                st.session_state["vi4"] = [
                    temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc]
            st.bokeh_chart(plt_vi4.makePlotVI(st.session_state["vi4"]))
            col1.markdown(plt_statetitle("vi4"), unsafe_allow_html=True)





            st.markdown(task_subtitle("Анализ результатов"), unsafe_allow_html=True)

            st.markdown(r'''
            Сравните полученные графики и ответьте на следующие вопросы:
            <ol class="rectangle-list">
            <li>Как напряжение топливного элемента V меняется с изменением давления p?</li>
            <li>Как Вы думаете, соответствует ли V(p) принципу Ле Шателье?</li>
            </ol>
            ''', unsafe_allow_html=True)


if tab_selected == works[1] and lang_selected == "ENG":

    # st.session_state["work"] = 1

    cflag = False

    if cflag:
        st.markdown('''
        Under construction...
        ''')
    else:


        with st.container():
            st.header("Effect of temperature on the performance of fuel cell")
            st.markdown('''
            <div style="text-align: justify;">              
            The ideal performance of a fuel cell depends on the electrochemical reactions that occur with different fuels and oxygen.
            Standard-state reversible fuel cell voltages (E<sub>0</sub> values) are only useful under standard-state conditions (room temperature, atmospheric pressure, unit activities of all species).
            Fuel cells are frequently operated under conditions that vary greatly from the standard state. For example, high-temperature fuel cells operate at 700–1000°C,
            automotive fuel cells often operate under 3–5 atm of pressure, and almost all fuel cells cope with variations in the concentration (and therefore activity) of reactant species.
            In the following sections, we systematically define how reversible fuel cell voltages are affected by departures from the standard state.
            First, the influence of temperature on the reversible fuel cell voltage will be explored, then the influence of pressure.           
            <p></p></div>
            ''', unsafe_allow_html=True)


        
            with st.container():  
                
                st.markdown('''
                To understand how the reversible voltage varies with temperature, lets look at the differential expression for the Gibbs free energy (G) - one of
                the most important themodynamic relation for chemical reactions in the fuel cell:
                ''')



                st.latex(r'''
                \tag{1} dG = −SdT + Vdp
                ''')

                st.markdown(''' 
                <div style="text-align: justify;">
                <p>     
                where S is entropy, T, V and p - are thermodynamic parameters (temperature, volume and pressure).  
                </p>
                <p>
                From the equation (1), it is possible to find the relation between molar reaction quantities g and s:
                </p></div>
                ''', unsafe_allow_html=True)

                st.latex(r'''
                \tag{2} \left(\frac{d (\Delta g)}{dT}
                \right)_p = −\Delta s
                ''')

                st.markdown('''
                The Gibbs free energy Δg is related to the cell voltage E, Faraday constant F 
                and the number of moles of transferred electrons n by the equation:
                ''')

                st.latex(r'''
                \tag{3} \Delta g = -nFE
                ''')   

                st.markdown('''
                When we combine the previous expressions (2) and (3) we can find how a fuel cell voltage E varies as a function of temperature:
                ''')         

                st.latex(r'''
                \tag{4} \left(\frac{dE}{dT}\right)_p = \frac{\Delta s}{nF}
                ''')   


                st.markdown('''
                or in intagrated form:
                ''')

                st.latex(r'''
                \tag{5} E_T=E_0+ nF \cdot \Delta s \cdot (T−T_0) 
                ''')   


                st.markdown('''
                where E<sub>T</sub> – is the reversible cell voltage at an arbitrary temperature T and constant pressure.
                Generally, we assume Δs to be independent of temperature. If a more accurate value of E<sub>T</sub> is required, it may be 
                calculated by integrating the heat-capacity-related temperaturedependence of Δs.
                ''', unsafe_allow_html=True)

                st.markdown('''
                A task below wil help you to understand the influence of working temperature on the fuel cell voltage.
                ''')


                st.markdown(task_title("Task 1.1","Low and high temperatures"), unsafe_allow_html=True)

                st.markdown(task_subtitle("Simulations"), unsafe_allow_html=True)

                st.markdown('''
                * Using the sliders at the `Model parameters` panel change cell temperature to 700 K. 
                * Check `Allow to refresh` flag and press `Run simulation` button under the panel.
                * Plot in figure below should update. Uncheck `Allow to refresh` flag to freeze any chages on the plot.
                ''')




            
                col1, col2 = st.columns([2,1])
                chk_vi1 = col2.checkbox(td[lang_selected][14], key="chk_vi1")
                if chk_vi1 and btn_runsimulation:
                    st.session_state["vi1"] = [
                        temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc]
                st.bokeh_chart(plt_vi1.makePlotVI(st.session_state["vi1"]))
                col1.markdown(plt_statetitle("vi1"), unsafe_allow_html=True)


                st.markdown('''
                * Using the sliders at the `Model parameters` panel change cell temperature to 900 K. 
                * Check `Allow to refresh` flag and press `Run simulation` button under the panel.
                * Plot in figure below should update. Uncheck `Allow to refresh` flag to freeze any chages on the plot.
                ''')


                col1, col2 = st.columns([2,1])
                chk_vi2 = col2.checkbox(td[lang_selected][14], key="chk_vi2")
                if chk_vi2 and btn_runsimulation:
                    st.session_state["vi2"] = [
                        temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc]

                st.bokeh_chart(plt_vi2.makePlotVI(st.session_state["vi2"]))
                col1.markdown(plt_statetitle("vi2"), unsafe_allow_html=True)

                st.markdown(task_subtitle("Results analysis"), unsafe_allow_html=True)


                st.markdown(r'''
                Compare the obtained Voltage-Current curves and answer the questions:
                <ol class="rectangle-list">
                <li>How does the fuel cell voltage V change with temperature T?</li>
                <li>How do the obtained results match with expression (5)?</li>
                </ol>
                ''', unsafe_allow_html=True)


            with st.container():

                st.header("Influence of pressure on fuel cell performance")

                st.markdown('''
                Like temperature effects, the pressure effects on cell voltage may also be calculated starting from the
                differential expression for the Gibbs free energy (1) and its electrochemical definition (3): 
                ''', unsafe_allow_html=True)

                st.latex(r'''
                \left(\frac{dG}{dp}\right)_T = \Delta V \Rightarrow \left(\frac{d (\Delta g)}{dp}\right)_T = \Delta v 
                ''')

                st.markdown('''
                and, finally:
                ''')

                st.latex(r'''
                \tag{6} \left(\frac{dE}{dp}\right)_T = -\frac{\Delta v}{nF} 
                ''')

                st.markdown('''
                Expression (6) means the variation of the reversible cell voltage with pressure is related to the volume change of the reaction. 
                If the volume change of the reaction is negative (if fewer moles of gas are generated by the reaction than consumed, for instance), 
                then the cell voltage will increase with increasing pressure. This is an example of *Le Chatelier’s principle*: 
                Increasing the pressure of the system favors the reaction direction that relieves the stress on the system.
                ''')

                st.markdown('''
                To understand how the fuel cell  works at non-ambient pressure, complete the following tasks:
                ''')


                st.markdown(task_title("Task 1.2","Normal and high pressures"), unsafe_allow_html=True)

                st.markdown(task_subtitle("Simulations"), unsafe_allow_html=True)

                st.markdown('''
                * Using the sliders at the `Model parameters` panel change acting pressure value to 1.1 atm. 
                * Check `Allow to refresh` flag and press `Run simulation` button under the panel.
                * Plot in figure below should update. Uncheck `Allow to refresh` flag to freeze any chages on the plot.
                ''')

            
                col1, col2 = st.columns([2,1])
                chk_vi3 = col2.checkbox(td[lang_selected][14], key="chk_vi3")
                if chk_vi3 and btn_runsimulation:
                    st.session_state["vi3"] = [
                        temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc]
                st.bokeh_chart(plt_vi3.makePlotVI(st.session_state["vi3"]))
                col1.markdown(plt_statetitle("vi3"), unsafe_allow_html=True)
        

                st.markdown('''
                * Using the sliders at the `Model parameters` panel change acting pressure value to 1.8 atm. 
                * Check `Allow to refresh` flag and press `Run simulation` button under the panel.
                * Plot in figure below should update. Uncheck `Allow to refresh` flag to freeze any chages on the plot.
                ''')

            
                col1, col2 = st.columns([2,1])
                chk_vi4 = col2.checkbox(td[lang_selected][14], key="chk_vi4")
                if chk_vi4 and btn_runsimulation:
                    st.session_state["vi4"] = [
                        temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc]
                st.bokeh_chart(plt_vi4.makePlotVI(st.session_state["vi4"]))
                col1.markdown(plt_statetitle("vi4"), unsafe_allow_html=True)





                st.markdown(task_subtitle("Results analysis"), unsafe_allow_html=True)

                st.markdown(r'''
                Compare the obtained Voltage-Current curves and answer the questions:
                <ol class="rectangle-list">
                <li>How the fuel cell voltage V reacts on the pressure changing?</li>
                <li>Does V(p) follows th Le Chatelier's principle?</li>
                </ol>
                ''', unsafe_allow_html=True)





if tab_selected == works[2] and lang_selected == "RU":

   #  st.session_state["work"] = 2

    with st.container():
        st.header("Проводимость компонентов и ее влияние на работу ТОТЭ")
        st.markdown(r'''
        Омические потери (E<sub>Ohm</sub>) в топливном элементе являются результатом ионной проводимости через электролит и электрического сопротивления, 
        оказываемого потоку электронов во внешней электрической цепи. Это неотъемлемое свойство кристаллических материалов. 
        Чтобы снизить омические потери, а следовательно, максимизировать ионную проводимость, можно воспользоваться следующими методами:
        <ol>
        <li>работа при более высоких температурах;</li>
        <li>использование замещающего легирования для дальнейшего улучшения кристаллической структуры материала и контроля концентрации дефектов</li>
        <li>уменьшение толщины электролита.</li>
        </ol>
        ''', unsafe_allow_html=True)

        st.markdown(r'''
        Общее выражение для термических потерь задаётся законом Ома:
        ''')

        st.latex(r'''
        \tag{1} E_{\text{Ohm}}=R_{\text{Ohm}} \cdot I
        ''')

        st.markdown(r'''
        где сопротивление R<sub>Ohm</sub> зависит от внутренних характеристик материалов топливного элемента как проводников тока, в частности удельной 
        проводимости электролита σ и толщины электролита d:
        ''', unsafe_allow_html=True)

        st.latex(r'''
        \tag{2} R_{\text{Ohm}} =\frac{\delta}{\sigma}
        ''')

        st.markdown('''
        Удельная проводимость твёрдого оксида, как правило, зависит от температуры и определяется следующим образом:
        ''')

        st.latex(r'''
        \tag{3} \sigma = \sigma_0 \cdot e^{-A/RT}
        ''')

        st.markdown('''
        где σ<sub>0</sub> и A – параметры, определяемые природой электролита, T – температура электролита, R – универсальная газовая постоянная. 
        ''', unsafe_allow_html=True)


        st.markdown('''
        Приведённое ниже задание поможет Вам понять влияние удельной проводимости электролита на омические потери топливного элемента:
        ''')

        with st.container():

            st.markdown(task_title("Задание 2.1","Роль удельной проводимости электролита на омические потери топливного элемента"), unsafe_allow_html=True)

            st.markdown(task_subtitle("Работа с моделью"), unsafe_allow_html=True)

            st.markdown(r'''
            * На боковой панели `Параметры модели` установите удельную проводимость σ на 0.2 См/м.
            * Установите флажок на функцию `Обновлять график` над графиком ниже и нажмите на кнопку `Запуск симуляции` внизу боковой панели.
            * График обновится. Снимите флажок с функции `Обновлять график`, чтобы зафиксировать полученные результаты.
            ''')

            
            col1, col2 = st.columns([2,1])
            chk_vi5 = col2.checkbox(td[lang_selected][14], key="chk_vi5")
            if chk_vi5 and btn_runsimulation:
                st.session_state["vi5"] = [
                    temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc]
            st.bokeh_chart(plt_vi5.makePlotVI(st.session_state["vi5"]))
            col1.markdown(plt_statetitle("vi5"), unsafe_allow_html=True)



            st.markdown('''
            * На боковой панели `Параметры модели` установите удельную проводимость σ на 2.5 См/м.
            * Установите флажок на функцию `Обновлять график` над графиком ниже и нажмите на кнопку «Запуск симуляции» внизу боковой панели.
            * График обновится. Снимите флажок с функции `Обновлять график`, чтобы зафиксировать полученные результаты.
            ''')

            col1, col2 = st.columns([2,1])
            chk_vi6 = col2.checkbox(td[lang_selected][14], key="chk_vi6")
            if chk_vi6 and btn_runsimulation:
                st.session_state["vi6"] = [
                    temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc]
            st.bokeh_chart(plt_vi6.makePlotVI(st.session_state["vi6"]))
            col1.markdown(plt_statetitle("vi6"), unsafe_allow_html=True)


            st.markdown(task_subtitle("Анализ результатов"), unsafe_allow_html=True)

        

            st.markdown(r'''
            Сравните полученные графики и ответьте на следующие вопросы:
            <ol class="rectangle-list">
            <li>Как увеличение удельной проводимости влияет на эффективность топливного элемента?</li>
            <li>В какой область токов кривая V(I) меняется сильнее всего при варьировании σ?</li>
            </ol>
            ''', unsafe_allow_html=True)



        with st.container(): 

            st.markdown('''<p></p>''', unsafe_allow_html=True)

            st.markdown(task_title("Задание 2.2","Роль толщины электролита на омические потери топливного элемента"), unsafe_allow_html=True)

            st.markdown(task_subtitle("Работа с моделью"), unsafe_allow_html=True)

            st.markdown(r'''
            * На боковой панели `Параметры модели` установите толщину электролита d на 30 мкм.
            * Установите флажок на функцию `Обновлять график` над графиком ниже и нажмите на кнопку `Запуск симуляции` внизу боковой панели.
            * График обновится. Снимите флажок с функции `Обновлять график`, чтобы зафиксировать полученные результаты.
            ''')
    
            col1, col2 = st.columns([2,1])
            chk_vi7 = col2.checkbox(td[lang_selected][14], key="chk_vi7")
            if chk_vi7 and btn_runsimulation:
                st.session_state["vi7"] = [
                    temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc]
            st.bokeh_chart(plt_vi7.makePlotVI(st.session_state["vi7"]))
            col1.markdown(plt_statetitle("vi7"), unsafe_allow_html=True)




            st.markdown(r'''
            * На боковой панели `Параметры модели` установите толщину электролита d на 150 мкм.
            * Установите флажок на функцию `Обновлять график` над графиком ниже и нажмите на кнопку `Запуск симуляции` внизу боковой панели.
            * График обновится. Снимите флажок с функции `Обновлять график`, чтобы зафиксировать полученные результаты.
            ''')

            col1, col2 = st.columns([2,1])
            chk_vi8 = col2.checkbox(td[lang_selected][14], key="chk_vi8")
            if chk_vi8 and btn_runsimulation:
                st.session_state["vi8"] = [
                    temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc]
            st.bokeh_chart(plt_vi8.makePlotVI(st.session_state["vi8"]))
            col1.markdown(plt_statetitle("vi8"), unsafe_allow_html=True)



            st.markdown(task_subtitle("Анализ результатов"), unsafe_allow_html=True)
            st.markdown(r'''
            Сравните полученные графики и ответьте на следующие вопросы:
            <ol class="rectangle-list">
            <li>Как увеличение толщины электролита влияет на эффективность топливного элемента?</li>
            <li>Какова связь между d и σ при фиксированном напряжении V?</li>
            </ol>
            ''', unsafe_allow_html=True)



if tab_selected == works[2] and lang_selected == "ENG":

    # st.session_state["work"] = 2

    cflag = False 

    if cflag:
        st.markdown('''
        Under construction...
        ''')
    else:

        with st.container():
            st.header("Ohmic losses")
            st.markdown(r'''
            Ohmic losses (E<sub>Ohm</sub>) in an SOFC result from ionic conductivity through the electrolyte and electrical resistance 
            offered to the flow of electrons in the external electrical circuit. This is inherently a materials property 
            of the crystal structure and atoms involved. However, to maximize the ionic conductivity, several methods 
            can be done. Firstly, operating at higher temperatures can significantly decrease these ohmic losses. 
            Substitutional doping methods to further refine the crystal structure and control defect concentrations 
            can also play a significant role in increasing the conductivity. Another way to decrease ohmic resistance 
            is to decrease the thickness of the electrolyte layer.
            ''', unsafe_allow_html=True)

            st.markdown(r'''
            An ionic specific resistance of the electrolyte as a function of temperature can be described by the following relationship:
            ''')

            st.latex(r'''
            \tag{1} E_{\text{Ohm}}=R_{\text{Ohm}} \cdot I
            ''')

            st.markdown(r'''
            where R<sub>Ohm</sub> depended from internal parameters of fuel cell materials, specsificaly σ (average area conductivity) and
            d (elrolyte thickness):
            ''', unsafe_allow_html=True)

            st.latex(r'''
            \tag{2} R_{\text{Ohm}} =\frac{\delta}{\sigma}
            ''')

            st.markdown('''
            The ionic conductivity of the solid oxide is defined as follows:
            ''')

            st.latex(r'''
            \tag{3} \sigma = \sigma_0 \cdot e^{-A/RT}
            ''')

            st.markdown('''
            where σ<sub>0</sub> and A is material dependent parameters, T is working temperature, R is gas constant. 
            ''', unsafe_allow_html=True)


            st.markdown('''
            Complete the following tasks:
            ''')

            with st.container():

                st.markdown(task_title("Task 2.1","Electrolyte conductivity and its role in Ohmic losses"), unsafe_allow_html=True)

                st.markdown(task_subtitle("Simulation"), unsafe_allow_html=True)

                st.markdown(r'''
                * Using the slides at the `Model parameters` panel set parameter σ to 0.2 S/m.
                * Check `Allow to refresh` flag and press `Run simulation` button under the panel.
                * Plot in figure below should update. Uncheck `Allow to refresh` flag to freeze any chages on the plot.
                ''')

                
                col1, col2 = st.columns([2,1])
                chk_vi5 = col2.checkbox(td[lang_selected][14], key="chk_vi5")
                if chk_vi5 and btn_runsimulation:
                    st.session_state["vi5"] = [
                        temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc]
                st.bokeh_chart(plt_vi5.makePlotVI(st.session_state["vi5"]))
                col1.markdown(plt_statetitle("vi5"), unsafe_allow_html=True)



                st.markdown('''
                * Using the slides at the `Model parameters` panel set parameter σ to 2.5 S/m.
                * Check `Allow to refresh` flag and press `Run simulation` button under the panel.
                * Plot in figure below should update. Uncheck `Allow to refresh` flag to freeze any chages on the plot.
                ''')

                col1, col2 = st.columns([2,1])
                chk_vi6 = col2.checkbox(td[lang_selected][14], key="chk_vi6")
                if chk_vi6 and btn_runsimulation:
                    st.session_state["vi6"] = [
                        temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc]
                st.bokeh_chart(plt_vi6.makePlotVI(st.session_state["vi6"]))
                col1.markdown(plt_statetitle("vi6"), unsafe_allow_html=True)


                st.markdown(task_subtitle("Result analysis"), unsafe_allow_html=True)

            

                st.markdown(r'''
                Compare the obtained Voltage-Current curves  and answer the questions:
                <ol class="rectangle-list">
                <li>How does an increase in conductivity affect the efficiency of a fuel cell? </li>
                <li>In which range of currents the V (I) curve changes significantly with σ?</li>
                </ol>
                ''', unsafe_allow_html=True)



            with st.container(): 

                st.markdown('''<p></p>''', unsafe_allow_html=True)

                st.markdown(task_title("Task 2.2","Electrolyte thickness and its role in  Ohmic losses"), unsafe_allow_html=True)

                st.markdown(task_subtitle("Simulation"), unsafe_allow_html=True)

                st.markdown(r'''
                * Using the slides at the `Model parameters` panel set parameter d to 30 µm.
                * Check `Allow to refresh` flag and press `Run simulation` button under the panel.
                * Plot in figure below should update. Uncheck `Allow to refresh` flag to freeze any chages on the plot.
                ''')
        
                col1, col2 = st.columns([2,1])
                chk_vi7 = col2.checkbox(td[lang_selected][14], key="chk_vi7")
                if chk_vi7 and btn_runsimulation:
                    st.session_state["vi7"] = [
                        temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc]
                st.bokeh_chart(plt_vi7.makePlotVI(st.session_state["vi7"]))
                col1.markdown(plt_statetitle("vi7"), unsafe_allow_html=True)




                st.markdown(r'''
                * Using the slides at the `Model parameters` panel set parameter d to 150 µm.
                * Check `Allow to refresh` flag and press `Run simulation` button under the panel.
                * Plot in figure below should update. Uncheck `Allow to refresh` flag to freeze any chages on the plot.
                ''')

                col1, col2 = st.columns([2,1])
                chk_vi8 = col2.checkbox(td[lang_selected][14], key="chk_vi8")
                if chk_vi8 and btn_runsimulation:
                    st.session_state["vi8"] = [
                        temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc]
                st.bokeh_chart(plt_vi8.makePlotVI(st.session_state["vi8"]))
                col1.markdown(plt_statetitle("vi8"), unsafe_allow_html=True)



                st.markdown(task_subtitle("Result analysis"), unsafe_allow_html=True)
                st.markdown(r'''
                Compare the resulting graphs and answer the following questions: 
                <ol class="rectangle-list">
                <li>How does an increase in electrolyte thickness affect the efficiency of a fuel cell?</li>
                <li>What is the relationship between d and σ [when V value is fixed]?</li>
                </ol>
                ''', unsafe_allow_html=True)



if tab_selected == works[3] and lang_selected == "RU":

    # st.session_state["work"] = 3

    with st.container():

        st.header("Массоперенос в ТОТЭ")
 
        st.markdown('''
        <div style="text-align: justify;">
        <p>        
        Для того, чтобы генерировать электричество, топливный элемент должен постоянно снабжаться  как топливом , так и окислителем.
        В тоже время, вода, как продукт химической реакции, должны непрерывно удалься из рабочей области воизбежание потери в 
        производительности ТОТЭ.
        </p>
        <p>
        Процессы непрерывной подачи реагентов и удаления продуктов в топливных элементоах называется массопереносом. Плохой массовый транспорт приводит к значительным потерям в производительности топливных элементов. Все дело в том, что 
        производительность топливных элементов определяется концентрацией реагента и продукта в слое катализатора, а не на входе в топливный элемент. Таким образом, истощение реагентов (или накопление продукта) в слое катализатора 
        будет отрицательно влиять на производительность. Такие потери в производительности топливного элемента называется <i>концентационными</i> (E<sub>con</sub>).
        </p> 
        Как правило, концентрационные поляризационные потери иногда выражаются как функция предельного тока, j<sub>m</sub>,
        которая является мерой максимальной скорости, с которой реагент может подаваться на электроды: 
        </div>
        ''', unsafe_allow_html=True)

        st.latex(r'''
        \tag{1} E_{\text{con}} = \frac{RT}{2F}\cdot\ln\left(\frac{j_m}{j_m-j}\right)
        '''
        )


        st.markdown('''
        <div style="text-align: justify;">        
        Используя модель ТОТЭ, выполните следующее задание: 
        <p></p></div>
        ''', unsafe_allow_html=True)


    with st.container():


        st.markdown(task_title("Задание 3.1","Влияние параметра j<sub>m</sub> на работу ТОТЭ"), unsafe_allow_html=True)

        st.markdown(task_subtitle("Работа с моделью"), unsafe_allow_html=True)

    
        st.markdown('''
        * На боковой панели `Параметры модели` установите значение лимитирующего тока равным  60 мА/cм².
        * Установите флажок на функцию `Обновлять график` над графиком ниже и нажмите на кнопку `Запуск симуляции` внизу боковой панели.
        * График обновится. Снимите флажок с функции `Обновлять график`, чтобы зафиксировать полученные результаты. 
        ''')



        col1, col2 = st.columns([2,1])
        chk_pi1 = col2.checkbox(td[lang_selected][14], key="chk_pi1")
        if chk_pi1 and btn_runsimulation:
            st.session_state["pi1"] = [
                temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc]
        st.bokeh_chart(plt_pi1.makePlotPI(st.session_state["pi1"]))
        col1.markdown(plt_statetitle("pi1"), unsafe_allow_html=True)

    with st.container():

        st.markdown('''
        * На боковой панели `Параметры модели` установите значение лимитирующего тока равным  100 мА/cм².
        * Установите флажок на функцию `Обновлять график` над графиком ниже и нажмите на кнопку `Запуск симуляции` внизу боковой панели.
        * График обновится. Снимите флажок с функции `Обновлять график`, чтобы зафиксировать полученные результаты. 
        ''')

        col1, col2 = st.columns([2,1])
        chk_pi2 = col2.checkbox(td[lang_selected][14], key="chk_pi2")
        if chk_pi2 and btn_runsimulation:
            st.session_state["pi2"] = [
                temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc]
        st.bokeh_chart(plt_pi2.makePlotPI(st.session_state["pi2"]))
        col1.markdown(plt_statetitle("pi2"), unsafe_allow_html=True)
        

        st.markdown(task_subtitle("Анализ результатов"), unsafe_allow_html=True)
        st.markdown(r'''
        Сравните полученные графики P(I) и ответьте на следующие вопросы:
        <ol class="rectangle-list">
        <li> Попробуйте объяснить,  каким именно образом варьирование j<sub>m</sub> влияет на эффективность ТОТЭ?</li>
        <li>В какой области токов влияние концентрационных потерь существенно сказывается на работе элемента, а где им можно пренебречь?</li>
        </ol>
        ''', unsafe_allow_html=True)


if tab_selected == works[3] and lang_selected == "ENG":

    # st.session_state["work"] = 3

    cflag = False 

    if cflag:
        st.markdown('''
        Under construction...
        ''')
    else:

        with st.container():

            st.header("Mass transport losses")
    
            st.markdown('''
            <div style="text-align: justify;">
            <p>     
            To produce electricity, a fuel cell must be continually supplied with fuel and oxidant. 
            At the same time, products must be continuously removed so as to avoid “strangling” the cell. 
            The process of supplying reactants and removing products is termed fuel cell mass transport. 
            As you will learn, this seemingly simple task can turn out to be quite complicated.
            </p>

            <p> 
            Why are we so interested in fuel cell mass transport? The answer is because poor mass transport leads to significant fuel cell performance losses. 
            To understand why poor mass transport can lead to a performance loss, remember that fuel cell performance 
            is determined by the reactant and product concentrations within the catalyst layer, not at the fuel cell inlet. 
            Thus, reactant depletion (or product accumulation) within the catalyst layer will adversely affect performance. 
            This loss in performance is called a fuel cell  <i>concentration</i> (E<sub>con</sub>) loss.
            </p>
            <p>
            Concentration polarization losses are sometimes expressed as a function of the limiting current, j<sub>m</sub>,,
            which is usually taken as a measure of the maximum rate atwhich a reactant can be supplied to an electrode:
            </p>
            </div>
            ''', unsafe_allow_html=True)

            st.latex(r'''
            \tag{1} E_{\text{con}} = \frac{RT}{2F}\cdot\ln\left(\frac{j_m}{j_m-j}\right)
            '''
            )


            st.markdown('''
            <div style="text-align: justify;">        
            To understand the influnce of the limiting current on the performance of the fuel cell complete the tollowing task.
            <p></p></div>
            ''', unsafe_allow_html=True)


        with st.container():


            st.markdown(task_title("Task 3.1","Influence of j<sub>m</sub> on SOFC performance"), unsafe_allow_html=True)

            st.markdown(task_subtitle("Sumulation"), unsafe_allow_html=True)

        
            st.markdown('''
            * Using the  `Model parameters` on the sidebar set limit current to 60 mA/cm².
            * Check `Allow to refresh` flag and press `Run simulation` button under the panel.
            * Plot in figure below should update. Uncheck `Allow to refresh` flag to freeze any chages on the plot.
            ''')



            col1, col2 = st.columns([2,1])
            chk_pi1 = col2.checkbox(td[lang_selected][14], key="chk_pi1")
            if chk_pi1 and btn_runsimulation:
                st.session_state["pi1"] = [
                    temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc]
            st.bokeh_chart(plt_pi1.makePlotPI(st.session_state["pi1"]))
            col1.markdown(plt_statetitle("pi1"), unsafe_allow_html=True)

        with st.container():

            st.markdown('''
            * Using the  `Model parameters` on the sidebar set limit current to 100 mA/cm².
            * Check `Allow to refresh` flag and press `Run simulation` button under the panel.
            * Plot in figure below should update. Uncheck `Allow to refresh` flag to freeze any chages on the plot.
            ''')

            col1, col2 = st.columns([2,1])
            chk_pi2 = col2.checkbox(td[lang_selected][14], key="chk_pi2")
            if chk_pi2 and btn_runsimulation:
                st.session_state["pi2"] = [
                    temperature, pressure, sigma, ethick, jm, H2ac, H2Oac, O2cc]
            st.bokeh_chart(plt_pi2.makePlotPI(st.session_state["pi2"]))
            col1.markdown(plt_statetitle("pi2"), unsafe_allow_html=True)
            

            st.markdown(task_subtitle("Result analysis"), unsafe_allow_html=True)
            st.markdown(r'''
            Compare two P(I) plots and answer the following questions
            <ol class="rectangle-list">
            <li>Try to explain how the variation of j<sub>m</sub> affects the SOFC efficiency?</li>
            <li>In what range of currents does the influence of concentration losses significantly affect the operation of the element, and when can it be neglected?</li>
            </ol>
            ''', unsafe_allow_html=True)
        






for k, v in zip([
    "ni_fuel_gas",
    "ni_eff_value",
    "ni_gen_power",
    "ni_gen_adduct",
    ],[np.round(10.0,1), np.round(65.0,1), np.round(216.0,1), np.round(89.0,1)]):
    if k not in st.session_state:
        st.session_state[k] = v



def _update_on_change_fuel_gas():
    # st.session_state['ni_fuel_gas'] = st.session_state['ni_fuel_gas']
    # st.session_state['ni_eff_value'] = eff_value
    st.session_state['ni_gen_power'] = st.session_state['ni_fuel_gas']*st.session_state['ni_eff_value']/100.0*33.0
    st.session_state['ni_gen_adduct'] = st.session_state['ni_fuel_gas']*8.9360119
def _update_on_change_eff_value():
    # st.session_state['ni_fuel_gas'] = st.session_state['ni_fuel_gas']
    # st.session_state['ni_eff_value'] = eff_value
    # st.session_state['ni_gen_power'] = st.session_state['ni_fuel_gas']*st.session_state['ni_eff_value']/100.0*33.0
    # st.session_state['ni_gen_adduct'] = st.session_state['ni_fuel_gas']*8.9360119
    _update_on_change_fuel_gas()
def _update_on_change_gen_power():
    st.session_state['ni_fuel_gas'] = st.session_state['ni_gen_power']/st.session_state['ni_eff_value']*100.0/33.326
    # st.session_state['ni_eff_value'] = eff_value
    # st.session_state['ni_gen_power'] = st.session_state['ni_fuel_gas']*st.session_state['ni_eff_value']/100.0*33.0
    st.session_state['ni_gen_adduct'] = st.session_state['ni_fuel_gas']*8.9360119
def _update_on_change_gen_adduct():
    st.session_state['ni_fuel_gas'] = st.session_state['ni_gen_adduct']/8.9360119
    # st.session_state['ni_eff_value'] = eff_value
    st.session_state['ni_gen_power'] = st.session_state['ni_fuel_gas']*st.session_state['ni_eff_value']/100.0*33.326
    # st.session_state['ni_gen_adduct'] = st.session_state['ni_fuel_gas']*8.9360119




if tab_selected == works[4] and lang_selected == "RU":
    
    # st.session_state["work"] = 4

    with st.container():
        st.header("Расчет характеристик батарии ТОТЭ")
        st.markdown('''
        <div style="text-align: justify;"> 
        <p>  
        Выполнив предыдущие работы, вы убедились, что топливный элемент - это  не что иное, как преобразователь энергии,
        который конвертирует энергию химической связи в электричество. Часто водород (H<sub>2</sub>) используется в качестве топлива и превращается в воду 
        (H<sub>2</sub>O) однако, существуют топливные элементы  которые могут использовать и другие топливные газы, такие как метан (CH<sub>3</sub>).        
        </p>
        <p>
        Калькулятор, представленный ниже, позволит вам оценить суммарную энергию и количество воды, производимое топливным элементом 
        при сжигании водорода.
        </p></div>
        ''', unsafe_allow_html=True)



        # fuel_gas, eff_value, gen_power, gen_adduct = 0.0, 65.0, 0.0, 0.0

        col1, col2 = st.columns([1,1]) 
        fuel_gas = col1.number_input(td[lang_selected][20], value=np.round(st.session_state['ni_fuel_gas'],1), format="%.1f", min_value=0.0, step=0.1, key="ni_fuel_gas", on_change=_update_on_change_fuel_gas)
        eff_value = col2.number_input(td[lang_selected][21], value=np.round(st.session_state['ni_eff_value'],1), format="%.0f",  min_value=0.1, max_value=100.0, step=1.0, key="ni_eff_value", on_change=_update_on_change_eff_value)
        col1, col2 = st.columns([1,1])
        gen_power = col1.number_input(td[lang_selected][22], value=np.round(st.session_state['ni_gen_power'],1), format="%.1f", min_value=0.0, step=0.1, key="ni_gen_power", on_change=_update_on_change_gen_power)
        gen_adduct = col2.number_input(td[lang_selected][23], value=np.round(st.session_state['ni_gen_adduct'],1), format="%.1f", min_value=0.0, step=0.1, key="ni_gen_adduct", on_change=_update_on_change_gen_adduct)


        # st.session_state['fuel_gas'] = fuel_gas
        # st.session_state['eff_value'] = eff_value
        # st.session_state['gen_power'] = gen_power
        # st.session_state['gen_adduct'] = gen_adduct


    with st.container():

        st.markdown('''<p></p>''', unsafe_allow_html=True)

        st.markdown(task_title("Задание 4.1","Расчет характеристик энергоустановки"), unsafe_allow_html=True)

        st.markdown(task_subtitle("Работа с калькулятором"), unsafe_allow_html=True)
        st.markdown('''
        * Используя представленный выше калькулятор, посчитайте, какое количество топлива (газа водорода) понадобится для снабжения электроэнергией двухкомнатной 
        квартиры в которой проживает семья из трех человека? Средняя потребность одного человека в электроэнергии составляет около 63 кВтч в месяц. 
        ''')

        st.markdown(task_subtitle("Дополнительные воросы"), unsafe_allow_html=True)
        st.markdown(r'''
        <ol class="rectangle-list">
        <li>Какова будет стоимость месяца работы такой энергоустановки (средняя цена 1 кг водорода 800-1000 руб.)?</li>
        <li>Можно ли оценить, какое количество тепла будет генерировать такая энергоустановка?</li>
        </ol>
        ''', unsafe_allow_html=True)
        


if tab_selected == works[4] and lang_selected == "ENG":

    # st.session_state["work"] = 4

    cflag = False 

    if cflag:
        st.markdown('''
        Under construction...
        ''')
    else:

        with st.container():
            st.header("Calculator of SOFC power source")
            st.markdown('''
            <div style="text-align: justify;"> 
            <p>
            After completing the previous work, you made sure that a fuel cell is nothing more than an energy converter that 
            transfers the energy of a chemical bond into electricity. Often hydrogen (H<sub>2</sub>) is used as a fuel and transformed 
            into water (H<sub>2</sub>O), however, there are fuel cells that can work with other fuel gases such as methane (CH<sub>3</sub>). 
            </p>
            <p>            
            This calculator will allow you to estimate the total energy and amount of water produced by a fuel cell.  
            </p></div>
            ''', unsafe_allow_html=True)



            # fuel_gas, eff_value, gen_power, gen_adduct = 0.0, 65.0, 0.0, 0.0

            col1, col2 = st.columns([1,1]) 
            fuel_gas = col1.number_input(td[lang_selected][20], value=np.round(st.session_state['ni_fuel_gas'],1), format="%.1f", min_value=0.0, step=0.1, key="ni_fuel_gas", on_change=_update_on_change_fuel_gas)
            eff_value = col2.number_input(td[lang_selected][21], value=np.round(st.session_state['ni_eff_value'],1), format="%.0f",  min_value=0.1, max_value=100.0, step=1.0, key="ni_eff_value", on_change=_update_on_change_eff_value)
            col1, col2 = st.columns([1,1])
            gen_power = col1.number_input(td[lang_selected][22], value=np.round(st.session_state['ni_gen_power'],1), format="%.1f", min_value=0.0, step=0.1, key="ni_gen_power", on_change=_update_on_change_gen_power)
            gen_adduct = col2.number_input(td[lang_selected][23], value=np.round(st.session_state['ni_gen_adduct'],1), format="%.1f", min_value=0.0, step=0.1, key="ni_gen_adduct", on_change=_update_on_change_gen_adduct)


            # st.session_state['fuel_gas'] = fuel_gas
            # st.session_state['eff_value'] = eff_value
            # st.session_state['gen_power'] = gen_power
            # st.session_state['gen_adduct'] = gen_adduct


        with st.container():

            st.markdown('''<p></p>''', unsafe_allow_html=True)

            st.markdown(task_title("Task 4.1","Characteristics of the SOFC power source"), unsafe_allow_html=True)

            st.markdown(task_subtitle("Calculations"), unsafe_allow_html=True)
            st.markdown('''
            * Using the calculator above, calculate how much fuel (hydrogen gas) will you need to power a two-room apartment in which a family of three people? 
            The average electricity requirement per person is about 63 kWh per month. 
            ''')

            st.markdown(task_subtitle("Additional questions"), unsafe_allow_html=True)
            st.markdown(r'''
            <ol class="rectangle-list">
            <li>What will be the cost of a month of operation of such a power plant (the average price of 1 kg of hydrogen is 11-14 USD)?</li>
            <li>Is it possible to estimate how much heat such a power plant will generate?</li>
            </ol>
            ''', unsafe_allow_html=True)
            

    

 



# if tab_selected == works[6]:
#     introduction_container = st.container()


if 'journal' not in st.session_state:
    st.session_state.journal = []

# 2 --- you can add some css to your Streamlit app to customize it
# TODO: Change values below and observer the changes in your app
# st.markdown(
#         f"""
# <style>
#     .reportview-container .main .block-container{{
#         max-width: 90%;
#         padding-top: 5rem;
#         padding-right: 5rem;
#         padding-left: 5rem;
#         padding-bottom: 5rem;
#     }}
#     img{{
#     	max-width:40%;
#     	margin-bottom:40px;
#     }}
# </style>
# """,
#         unsafe_allow_html=True,
#     )
#######################################
