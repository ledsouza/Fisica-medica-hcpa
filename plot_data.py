import pandas as pd
import plotly.graph_objects as go

def plot_atividade_administrada(cleaned_bi: pd.DataFrame):

    plot_bi = cleaned_bi.copy()
    plot_bi['Atividade Administrada (str)'] = plot_bi['Atividade Administrada'].astype(str).str.replace('.', ',')
    plot_bi['Dose (str)'] = plot_bi['Dose (mSv)'].astype(str).str.replace('.', ',')
    
    exame = cleaned_bi['Nome da definição do procedimento'].values[0]
    
    
    atividade_max = 30
    atividade_min = 20
    data_inicio = cleaned_bi['Mês'].values[0]
    data_fim = cleaned_bi['Mês'].values[-1]
    title_text = f"Atividade Administrada em cada solicitação de exame<br><sup size=16>Paciente Adulto com idade acima de 18 anos, Isótopo: Tc-99m, Fármaco: MDP<br>Perído: {data_inicio} a {data_fim}</sup>"

    fig = go.Figure(
        data=go.Scatter(
            x=cleaned_bi["Número da Solicitação do Exame"],
            y=cleaned_bi["Atividade Administrada"],
            mode="markers",
            name="",
            text=cleaned_bi["Código ID do Paciente"],
            customdata=plot_bi["Atividade Administrada (str)"],
            hovertemplate="<b>Código ID do Paciente</b>: %{text}<br><b>Atividade Administrada</b>: %{customdata} mCi",
        )
    )

    fig.update_layout(
        title=title_text,
        title_font=dict(size=18),
        xaxis_title="",
        yaxis_title="Atividade Administrada [mCi]",
        xaxis=dict(
            range=[0, cleaned_bi["Número da Solicitação do Exame"].max()],
            tickmode="array",
            tickvals=[],
            fixedrange=True,
        ),
        height=600,
        width=1500
    )

    fig.add_shape(
        type="line",
        x0=0,
        y0=atividade_max,
        x1=1,
        y1=atividade_max,
        xref="paper",
        line=dict(color="red", dash="dot"),
    )

    fig.add_shape(
        type="line",
        x0=0,
        y0=atividade_min,
        x1=1,
        y1=atividade_min,
        xref="paper",
        line=dict(color="red", dash="dot"),
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # fator_conversao = 0.15
    # dose_max = atividade_max * fator_conversao
    # dose_min = atividade_min * fator_conversao

    # title_text = f"Dose recebida pelo paciente em cada solicitação de exame<br><sup size=16>Paciente Adulto com idade acima de 18 anos, Isótopo: Tc-99m, Fármaco: MDP<br>Perído: {data_inicio} a {data_fim}</sup>"

    # fig = go.Figure(
    #     data=go.Scatter(
    #         x=cleaned_bi["Número da Solicitação do Exame"],
    #         y=cleaned_bi["Dose (mSv)"],
    #         mode="markers",
    #         name='',
    #         text=cleaned_bi["Código ID do Paciente"],
    #         customdata=plot_bi['Dose (str)'],
    #         hovertemplate="<b>Código ID do Paciente</b>: %{text}<br><b>Atividade Administrada</b>: %{customdata} mSv",
    #     )
    # )

    # fig.update_layout(
    #     title=title_text,
    #     title_font=dict(size=18),
    #     xaxis_title="",
    #     yaxis_title="Dose [mSv]",
    #     xaxis=dict(
    #         range=[0, cleaned_bi["Número da Solicitação do Exame"].max()],
    #         tickmode="array",
    #         tickvals=[],
    #         fixedrange=True
    #     ),
    #     height=600,
    #     width=1500
    # )

    # fig.add_shape(
    #     type="line",
    #     x0=0,
    #     y0=dose_max,
    #     x1=1,
    #     y1=dose_max,
    #     xref='paper',
    #     line=dict(color="red", dash="dot")
    # )

    # fig.add_shape(
    #     type="line",
    #     x0=0,
    #     y0=dose_min,
    #     x1=1,
    #     y1=dose_min,
    #     xref='paper',
    #     line=dict(color="red", dash="dot")
    # )

    # st.plotly_chart(fig, use_container_width=True)