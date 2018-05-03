# DNA Variant Report

O DNA Variant Report é um software livre escrito em Python 3.5.x que permite, com poucos cliques,
gerar um relatório de todas as variantes encontradas em uma amostra de DNA que já foram catalogadas
no site ClinVar.
Além de correlacionar as variantes de uma pessoa com a base de dados, é possível fazer diversas
buscas por informações importantes, seja diretamente um fenótipo (doenças), ou por significância clínica.
As opções de significância clínica são:

1. Benigno
2. Provável benigno
3. Patogênico
4. Provável patogênico
5. Variantes de significado incerto (VUS)
6. Outros

Para efetuar essa busca, o software necessita que seja baixada a base de dados do site do
[ClinVar](https://www.ncbi.nlm.nih.gov/clinvar/docs/maintenance_use/), mais especificamente, o arquivo separado
por tabulação **variant_summary.txt.gz**. De posse da base de dados, mais um arquivo **VCF**
(resultante de um exame de DNA), é possível efetuar as buscas.

Para executar tais operações, o programa utiliza as bibliotecas:

1. [Pandas](https://pandas.pydata.org/)
2. [PyQt5](https://www.riverbankcomputing.com/software/pyqt/download5)
3. [PyVCF](http://pyvcf.readthedocs.io/)

Tendo sido feitas as buscas necessárias, e aplicados os filtros definidos pelo usuário, é possível
salvar o relatório em formato XLS, utilizando a biblioteca [xlwt](https://pypi.org/project/xlwt/).

#### Instalação

Até o presente momento, o software foi instalado apenas em sistemas operacionais Linux, baseados
na distribuição Ubuntu (16.04). Para instalar as dependências necessárias, basta executar o comando
abaixo em um terminal (como root/sudo):

    apt install python3 python3-pandas python3-pyqt5 python3-numpy python3-pip

Caso deseje poder exportar os relatórios, é necessário também instalar o **xlwt**:

    pip3 install xlwt

Finalmente, dê permissão de execução para o programa com o comando (estando na mesma pasta do programa):

    chmod +x dnavariantreport.py

##### Uso

Ao abrir o programa, o usuário possui poucas opções na tela:

![Tela inicial](docs/images/im1.png)

Assim, antes de utilizar o programa de fato, é necessário primeiro carregar os dados:

* Ir no menu e carregar a base de dados (compactada como gz)
* Após, carregar o arquivo VCF de interesse

![Tela inicial](docs/images/im2.png)

Após a escolha do VCF, o programa pode demorar alguns instantes para ler todos os dados, isso é normal.

![Tela inicial](docs/images/im3.png)

Finalizada a leitura, o programa já terá isolado as variantes do VCF com as variantes registradas no ClinVar.
Nesse momento algumas opções serão exibidas na tela:

* Filtros: permitindo fazer algumas buscas específicas sobre doenças ou baseado em significância clínica
* Gráfico de significância: Exibe as porcentagens (para aquele filtro aplicado), e um gráfico de pizza

![Tela inicial](docs/images/im4.png)

Os filtros são cumulativos, então caso deseje fazer outra busca, é necessário clicar no botão *Limpar Filtros*.
Com os devidos filtros aplicados, finalmente é possível exportar o relatório (caso tenha sido instalada a
biblioteca *xlwt*).

Para as próximas sessões, o programa iniciará já com a base e o último VCF pré carregado. Caso deseje
analisar outra amostra, basta repetir o passo de importar VCF (idem para quando for baixar uma versão
atualizada da base de dados).

##### Sistemas Microsoft Windows

Mesmo não tento sido testado em ambientes Windows, o programa deve funcionar de modo igual, tendo
sido cumpridas as dependências necessárias. Algumas bibliotecas podem ser instaladas diretamente via
**pip**, no entanto, para outras pode ser necessário buscar informações diretamente no site do desenvolvedor.

---

Desenvolvido por: **Kleydson Stenio** <kleydson.stenio@gmail.com> @ 2018