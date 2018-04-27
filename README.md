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
[ClinVar](ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/), mais especificamente, o arquivo separado
por tabulação **variant_summary.txt.gz**. De posse da base de dados, mais um arquivo **VCF**
(resultante de um exame de DNA), é possível efetuar as buscas.

Para executar tais operações, o programa utiliza as bibliotecas:

1. [Pandas](https://pandas.pydata.org/)
2. [PyQt5](https://www.riverbankcomputing.com/software/pyqt/download5)
3. [PyVCF](http://pyvcf.readthedocs.io/)

Tendo sido feitas as buscas necessárias, e aplicados os filtros definidos pelo usuário, é possível
salvar o relatório em formato XLS, utilizando a bilioteca [xlwt](https://pypi.org/project/xlwt/).

#### Instalação

Até o presente momento, o software foi instalado apenas em sistemas operacionais Linux, baseados
na distribuição Ubuntu (16.04). Para instalar as dependências necessárias, basta executar o comando
abaixo em um terminal (como root/sudo):

    apt install python3 python3-pandas python3-pyqt5 python3-numpy python3-pip

Caso deseje poder exportar os relatórios, é necessário também instalar o **xlwt**:

    pip3 install xlrd xlwt

Finalmente, dê permissão de execução para o programa com o comando (estando na mesma pasta do programa):

    chmod +x variantreport.py

##### Sistemas Microsoft Windows

Mesmo não tento sido testado em ambientes Windows, o programa deve funcionar de modo igual, tendo
sido cumpridas as dependências necessárias. Algumas bibliotecas podem ser instaladas diretamente via
**pip**, no entanto, para outras pode ser necessário buscar informações diretamente no site do desenvolvedor.

---

Desenvolvido por: **Kleydson Stenio** <kleydson.stenio@gmail.com> @ 2018