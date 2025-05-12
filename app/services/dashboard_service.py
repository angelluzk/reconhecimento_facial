from app.database.connection import get_db_connection

def get_dashboard_data():
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)

        # Total de alunos
        cursor.execute('SELECT COUNT(*) AS total_alunos FROM alunos')
        total_alunos = cursor.fetchone()['total_alunos']

        # Alunos com registro de entrada
        cursor.execute(''' 
            SELECT COUNT(DISTINCT id_aluno) AS alunos_ativos 
            FROM registros_presenca 
            WHERE tipo_registro = "entrada"
        ''')
        alunos_ativos = cursor.fetchone()['alunos_ativos']

        # Faltas recentes (sem entrada nos últimos 7 dias)
        cursor.execute(''' 
            SELECT COUNT(*) AS faltas_recent 
            FROM registros_presenca 
            WHERE tipo_registro = "saida" 
              AND data_hora >= NOW() - INTERVAL 7 DAY
        ''')
        faltas_recent = cursor.fetchone()['faltas_recent']

        # Entradas hoje
        cursor.execute(''' 
            SELECT COUNT(*) AS entradas_hoje 
            FROM registros_presenca 
            WHERE tipo_registro = "entrada" 
              AND DATE(data_hora) = CURDATE()
        ''')
        entradas_hoje = cursor.fetchone()['entradas_hoje']

        # Saídas hoje
        cursor.execute(''' 
            SELECT COUNT(*) AS saidas_hoje 
            FROM registros_presenca 
            WHERE tipo_registro = "saida" 
              AND DATE(data_hora) = CURDATE()
        ''')
        saidas_hoje = cursor.fetchone()['saidas_hoje']

        # Total de turmas
        cursor.execute('SELECT COUNT(DISTINCT turma) AS total_turmas FROM alunos')
        total_turmas = cursor.fetchone()['total_turmas']

        # Tempo médio de presença (em minutos) dos últimos 7 dias
        cursor.execute(''' 
            SELECT id_aluno, 
                MIN(CASE WHEN tipo_registro = 'entrada' THEN data_hora END) AS entrada,
                MAX(CASE WHEN tipo_registro = 'saida' THEN data_hora END) AS saida
            FROM registros_presenca
            WHERE data_hora >= NOW() - INTERVAL 7 DAY
            GROUP BY id_aluno
            HAVING entrada IS NOT NULL AND saida IS NOT NULL
        ''')
        tempos = cursor.fetchall()
        duracoes = [
            (r['saida'] - r['entrada']).total_seconds() / 60
            for r in tempos if r['saida'] and r['entrada']
        ]
        tempo_medio_presenca = round(sum(duracoes) / len(duracoes), 1) if duracoes else 0

        # Tempo mínimo entre registros (da tabela de configurações)
        cursor.execute("SELECT valor, tipo FROM configuracoes WHERE nome_configuracao = 'tempo_espera'")
        tempo_config = cursor.fetchone()
        tempo_espera = tempo_config['valor']
        tipo_espera = tempo_config['tipo']

        # Últimos registros de presença (limite 10)
        cursor.execute(''' 
            SELECT a.nome, r.tipo_registro, r.data_hora, r.turma
            FROM registros_presenca r
            JOIN alunos a ON r.id_aluno = a.id
            ORDER BY r.data_hora DESC
            LIMIT 10
        ''')
        ultimos_registros = cursor.fetchall()

        # Fotos recentes (últimas 12 reconhecidas)
        cursor.execute(''' 
            SELECT a.nome, a.turma, f.foto_nome
            FROM fotos_alunos f
            JOIN alunos a ON f.id_aluno = a.id
            ORDER BY f.id_foto DESC
            LIMIT 12
        ''')
        fotos_recentes = cursor.fetchall()

        for foto in fotos_recentes:
            foto['foto_url'] = '/storage/fotos_alunos/' + foto['foto_nome']


        # Dados para gráfico de presença por semana (últimos 7 dias úteis)
        cursor.execute(''' 
            SELECT DATE(data_hora) AS data, COUNT(*) AS total
            FROM registros_presenca
            WHERE tipo_registro = 'entrada'
              AND data_hora >= CURDATE() - INTERVAL 7 DAY
            GROUP BY DATE(data_hora)
            ORDER BY data ASC
        ''')
        dias_presenca = cursor.fetchall()
        semana_labels = [r['data'].strftime('%a') for r in dias_presenca]
        semana_totais = [r['total'] for r in dias_presenca]

        # Gráfico de distribuição por turno
        cursor.execute(''' 
            SELECT turno, COUNT(*) AS total
            FROM alunos
            GROUP BY turno
        ''')
        turnos = cursor.fetchall()
        turnos_labels = [r['turno'].capitalize() for r in turnos]
        turnos_totais = [r['total'] for r in turnos]
        turno_counts = dict(zip(turnos_labels, turnos_totais))

    taxa_reconhecimento = 98

    return {
        'total_alunos': total_alunos,
        'alunos_ativos': alunos_ativos,
        'faltas_recent': faltas_recent,
        'taxa_reconhecimento': taxa_reconhecimento,
        'entradas_hoje': entradas_hoje,
        'saidas_hoje': saidas_hoje,
        'total_turmas': total_turmas,
        'tempo_medio_presenca': tempo_medio_presenca,
        'tempo_espera': tempo_espera,
        'tipo_espera': tipo_espera,
        'ultimos_registros': ultimos_registros,
        'fotos_recentes': fotos_recentes,
        'grafico_presenca_labels': semana_labels,
        'grafico_presenca_dados': semana_totais,
        'grafico_turno_labels': turnos_labels,
        'grafico_turno_dados': turnos_totais,
        'semana_labels': semana_labels,
        'semana_presencas': semana_totais,
        'turno_counts': turno_counts
    }