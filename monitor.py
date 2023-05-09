import pandas as pd
from evidently.dashboard import Dashboard
from evidently.tabs import DataDriftTab, CatTargetDriftTab, RegressionPerformanceTab

# Carregue seus dados e previsões aqui
reference_data = pd.read_csv('reference_data.csv')
production_data = pd.read_csv('production_data.csv')
target = 'target_column'

# Configure as guias de monitoramento
tabs = [DataDriftTab, CatTargetDriftTab, RegressionPerformanceTab]

# Crie o painel de monitoramento
dashboard = Dashboard(tabs=tabs)
dashboard.calculate(reference_data, production_data, column_mapping=None, target=target)

# Salve o relatório HTML
with open('report.html', 'w') as f:
    f.write(dashboard.get_html())
