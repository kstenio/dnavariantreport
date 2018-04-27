#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, pickle;

sys.dont_write_bytecode = True  # não gera arquivos pyc
about = pickle.load(open('./About.bin', 'rb'))
#
#  dnavariantreport.py
#  
#  Copyright 2018 Kleydson Stenio <kleydson.stenio@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU Affero General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
import os, pandas, gzip, vcf, datetime
from numpy import uint32, round, bool, array
from PyQt5 import QtWidgets, uic
from PyQt5.Qt import QColor

# cria pasta para uso interno
if not os.path.isdir('./.variantreport-env'): os.mkdir('./.variantreport-env')

# carrega a interface gráfica
interface = uic.loadUiType('./dnavariantreport.ui')[0]

# define para mostrar tudo
pandas.set_option('display.max_colwidth', -1)

class DNAContultVariantReport_GUI(QtWidgets.QMainWindow, interface):
	def __init__(self, parent=None):
		# inicializa a classe/programa
		QtWidgets.QMainWindow.__init__(self, parent)
		self.setupUi(self)
		
		# configurações iniciais dos widgets
		self.extra_layout.setVisible(False)
		self.nomevcf_lb.setVisible(False)
		self.atualizalabelspizza(0, 0, 0, 0, 0, 100)
		
		# variáveis adicionais interessantes
		self.vcf, self.db, self.is_db, self.is_vcf = [], [], False, False
		self.linkeddb, self.linkedvcf, self.is_linked = [], [], False
		self.filtradodb, self.filtrado, self.filtradosig, self.filtros = [], False, [], []
		self.significancia = [[], [], [], [], [], [], [0, 0, 0, 0, 0, 0]]
		self.checkdb()
		self.checkvcf()
		self.linkdbvcf()
		
		# connects -> liga botões e outros elementos gráficos aos seus respectivos métodos
		self.actionSair.triggered.connect(self.closeEvent)
		self.actionSobre.triggered.connect(self.showAbout)
		self.actionExportarRET.triggered.connect(self.salvarelatorio)
		self.actionImportarDB.triggered.connect(self.importardb)
		self.actionImportarVCF.triggered.connect(self.importarvcf)
		self.significancia_cb.stateChanged.connect(lambda: self.habilitarfiltro(1))
		self.doenca_cb.stateChanged.connect(lambda: self.habilitarfiltro(2))
		self.filtros_pb.clicked.connect(self.aplicarfiltros)
		self.limpafiltros_pb.clicked.connect(self.limparfiltros)
		
	# ############### #
	# métodos de ação #
	# ############### #
	
	def loadqt(self, times):
		for i in range(times): QtWidgets.QApplication.processEvents()
	
	def checkdb(self):
		if os.path.isfile('./.variantreport-env/db.bin'):
			self.is_db = True
			self.db = pickle.load(open('./.variantreport-env/db.bin', 'rb'))
			self.estadobased_lb.setText('<html><b><span style=" color:#006622;">CARREGADA</spam></b></html>')
	
	def checkvcf(self):
		if os.path.isfile('./.variantreport-env/vcf.bin'):
			self.is_vcf = True
			self.vcf = pickle.load(open('./.variantreport-env/vcf.bin', 'rb'))
			self.nomevcf_lb.setText('<html><b><span style=" color:#c2d6d6;">Carregado da última análise</spam></b></html>')
			self.nomevcf_lb.setVisible(True)
			self.estadovcf_lb.setText('<html><b><span style=" color:#006622;">CARREGADO</spam></b></html>')
			if self.is_db:
				# libera o layout com as outras opções
				self.extra_layout.setVisible(True)
	
	def linkdbvcf(self):
		# executa apenas se ambos arquivos forem carregados
		if self.is_db and self.is_vcf:
			is_in_db = self.db.ID.isin(self.vcf.ID)
			self.linkeddb = self.db[is_in_db].drop_duplicates()
			self.is_linked = True
			self.criaboolsignificancia()
			
	def importardb(self):
		carregardb = True
		if self.is_db:
			question = QtWidgets.QMessageBox.question(self, 'Aviso',
			                                          'Já existe uma base de dados carregada.\n\nDeseja carregar outra?',
			                                          QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
			if question == QtWidgets.QMessageBox.Yes:
				carregardb = True
			else:
				carregardb = False
		if carregardb:
			arquivo = QtWidgets.QFileDialog.getOpenFileName(self, 'Selecione o arquivo com a base de dados', '.',
			                                                'Arquivos compactados gzip (*.gz)')
			if arquivo[0] != '':
				# prepara variáveis que serão utilizadas para ler e escrever os dados
				entrada, leitura = gzip.open(arquivo[0], 'rb'), []
				# lê cada linha do arquivo GZ
				for linha in entrada:
					linhadb = linha.decode('utf-8', 'backslashreplace').strip().split('\t')
					leitura.append([linhadb[9], linhadb[4], linhadb[18], linhadb[13].capitalize(), linhadb[6].capitalize()])
				entrada.close()
				# cria a base de dados do pandas
				self.db = pandas.DataFrame(leitura[1:], columns=['ID', 'Gene', 'Cromossomo', 'Fenótipo', 'Significância Clínica'])
				# carrega lista de categorias
				categorias = pickle.load(open('./ClinicalTypes.bin','rb'))
				# organiza melhor os tipos de cada
				self.db.ID = self.db.ID.replace(-1, 0).astype(uint32)
				self.db.Cromossomo = self.db.Cromossomo.astype('category')
				self.db.Gene = self.db.Gene.astype('category')
				self.db[self.db.columns[4]] = self.db[self.db.columns[4]].astype('category', categories=categorias, ordered=True)
				# dando tudo ok, salva a base de dados no programa, muda o status e avisa o usuário
				pickle.dump(self.db, open('./.variantreport-env/db.bin', "wb"))
				self.is_db = True
				self.estadobased_lb.setText('<html><b><span style=" color:#006622;">CARREGADA</spam></b></html>')
				QtWidgets.QMessageBox.information(self, 'Concluido!', 'Base de dados importada para o programa!')
	
	def criaboolsignificancia(self):
		# o booleano de significância é composto por 6 elementos, baseados no arquivo ClinicalTypes.bin
		# 0: benígno (0-10)
		# 1: provável benígno (11-26)
		# 2: patogênico (27-36)
		# 3: provável patogênico (37-47)
		# 4: incerto (48-54)
		# 5: outros (55-81)
		if self.filtrado:
			self.filtradosig = self.filtradodb
		else:
			self.filtradosig = self.linkeddb
		t = len(self.filtradosig[self.filtradosig.columns[4]])
		significancia = array(pandas.get_dummies(self.filtradosig[self.filtradosig.columns[4]]), dtype=bool)
		self.significancia[0] = significancia[:, 0:11].sum(1)
		self.significancia[1] = significancia[:, 11:27].sum(1)
		self.significancia[2] = significancia[:, 27:37].sum(1)
		self.significancia[3] = significancia[:, 37:48].sum(1)
		self.significancia[4] = significancia[:, 48:55].sum(1)
		self.significancia[5] = significancia[:, 55:].sum(1)
		self.significancia[6][0] = (self.significancia[0].sum() / t) * 100
		self.significancia[6][1] = (self.significancia[1].sum() / t) * 100
		self.significancia[6][2] = (self.significancia[2].sum() / t) * 100
		self.significancia[6][3] = (self.significancia[3].sum() / t) * 100
		self.significancia[6][4] = (self.significancia[4].sum() / t) * 100
		self.significancia[6][5] = (self.significancia[5].sum() / t) * 100
		self.significancia[6] = round(self.significancia[6], 3)
		return self.significancia[6]
	
	def importarvcf(self):
		if not self.is_db:
			QtWidgets.QMessageBox.critical(self, 'Erro', 'Importe a base de dados primeiro')
		carregarvcf = True
		if self.is_vcf and self.is_db:
			question = QtWidgets.QMessageBox.question(self, 'Aviso',
			                                          'Já foi carregado um arquivo VCF.\n\nDeseja carregar outro?',
			                                          QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
			if question == QtWidgets.QMessageBox.Yes:
				carregarvcf = True
			else:
				carregarvcf = False
		if carregarvcf and self.is_db:
			arquivo = QtWidgets.QFileDialog.getOpenFileName(self, 'Selecione o arquivo VCF', '.',
			                                                'Arquivos VCF (*.vcf)')
			if arquivo[0] != '':
				# prepara variáveis que serão utilizadas para ler e escrever os dados
				entrada, leitura, sep = vcf.Reader(open(arquivo[0], 'r')), [], ''
				# lê cada linha do arquivo VCF
				for linha in entrada:
					if linha.ID != None:
						sep = ',' if ',' in linha.ID else ';'
						leitura.append([linha.CHROM, linha.POS, linha.ID.split(sep)[0].replace('rs', ''), linha.REF[0],
						                linha.ALT[0], linha.QUAL, linha.FILTER, linha.INFO])
				# cria a base de dados do pandas
				self.vcf = pandas.DataFrame(leitura, columns=['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO'])
				# dando tudo ok, salva a base de dados no programa, muda o status e avisa o usuário
				pickle.dump(self.vcf, open('./.variantreport-env/vcf.bin', "wb"))
				self.is_vcf = True
				self.estadovcf_lb.setText('<html><b><span style=" color:#006622;">CARREGADO</spam></b></html>')
				self.nomevcf_lb.setText('<html><b><span style=" color:#c2d6d6;">%s</spam></b></html>' % (arquivo[0]))
				self.nomevcf_lb.setVisible(True)
				# reduz tamanho da base de dados
				self.vcf.ID = self.vcf.ID.replace(-1, 0).astype(uint32)
				self.vcf.CHROM = self.vcf.CHROM.astype('category')
				# cria novo dataframe, que é a intersecção entre os ID do VCF e DB
				self.linkdbvcf()
				# libera o layout com as outras opções
				self.extra_layout.setVisible(True)
				QtWidgets.QMessageBox.information(self, 'Concluido!', 'Arquivo VCF importado para o programa!')
				
	def showAbout(self):
		QtWidgets.QMessageBox.question(self, u'About the software', about, QtWidgets.QMessageBox.Ok)
	
	def closeEvent(self, event):
		try:
			event.accept()
		except AttributeError:
			QtWidgets.QApplication.quit()
	
	# ################### #
	# métodos de checagem #
	# ################### #
	
	def habilitarfiltro(self, flag):
		if flag == 1:
			if self.significancia_cb.isChecked():
				self.significancia_cbox.setEnabled(True)
			else:
				self.significancia_cbox.setEnabled(False)
		if flag == 2:
			if self.doenca_cb.isChecked():
				self.doenca_le.setEnabled(True)
			else:
				self.doenca_le.setEnabled(False)
	
	def limparfiltros(self):
		self.filtrado = False
		self.filtros = []
		self.limpafiltros_pb.setEnabled(False)
		self.limpafiltros_pb.setStyleSheet('')
		self.relatorio_te.clear()
		self.relatorio_te.setHtml('<b> <font color="dark blue">FILTROS LIMPOS</font> </b>')
		self.relatorio_lb.setText('Relatório do VCF (Sem filtros aplicados)')
		
		
	def aplicarfiltros(self):
		# aplica apenas se ambos arquivos forem carregados
		if self.is_db and self.is_vcf and self.is_linked:
			# libera o botão de limpar filtros
			self.limpafiltros_pb.setEnabled(True)
			self.limpafiltros_pb.setStyleSheet('color: #ffffff; background: #990000')
			
			# escolhe qual dataframe vai usar para fazer os filtros
			filtrado = []
			if not self.filtrado:
				filtrado = self.linkeddb.reset_index(drop=True)
			else:
				filtrado = self.filtradodb
				
			# caso tenha sido escolhido filtrar por significancia
			if self.significancia_cb.isChecked():
				self.criaboolsignificancia()
				filtrado = filtrado[self.significancia[self.significancia_cbox.currentIndex()].astype(bool)]
				self.filtros.append('Significância: %s' %(self.significancia_cbox.currentText()))
				self.filtrado = True
			
			# caso denha escolhido filtrar por doença
			elif self.doenca_cb.isChecked():
				chave, doenca = self.doenca_le.text(), []
				try:
					if len(chave) > 0:
						for i in range(len(filtrado[filtrado.columns[3]])):
							if (chave.lower() in filtrado[filtrado.columns[3]][i]) or (chave.capitalize() in filtrado[filtrado.columns[3]][i]):
								doenca.append(True)
							else:
								doenca.append(False)
						filtrado = filtrado[doenca].reset_index(drop=True)
						self.filtros.append('Doença: %s' %(self.doenca_le.text()))
						self.filtrado = True
				except KeyError: pass
			
			# faz o print com ou sem filtro
			self.filtradodb = filtrado
			self.relatorio_te.clear()
			self.relatorio_te.setHtml('<b> <font color="red">APLICANDO FILTROS...</font> </b>')
			self.loadqt(1)
			self.relatorio_te.setHtml(self.filtradodb.to_html())
			self.relatorio_lb.setText('Relatório do VCF (%s)' %(self.filtros))
			
			# atualiza o diagrama de pizza e os labels
			if len(self.filtradodb) is not 0:
				[b, lb, p, lp, i, o] = self.criaboolsignificancia()
				self.atualizalabelspizza(b, lb, p, lp, i, o)
			else:
				self.atualizalabelspizza(0, 0, 0, 0, 0, 100)
				
	def salvarelatorio(self):
		# salva apenas se algumas operações já foram feitas
		if self.is_db and self.is_vcf and self.is_linked:
			# escolhe qual dataframe vai salvar
			if not self.filtrado:
				salvar = self.linkeddb
			else:
				salvar = self.filtradodb
			ext = ['Arquivo do Excel', 'xls']
			stringsalva = 'Relatorio_VCF_%s.%s' % (datetime.datetime.now().strftime('%m-%d-%Y_%H:%M'), ext[1])
			nomesalva = QtWidgets.QFileDialog.getSaveFileName(self, 'Selecione arquivo para salvar relatório',
			                                                  stringsalva, '%s (*.%s)' % (ext[0], ext[1]))
			if nomesalva[1] == '%s (*.%s)' %(ext[0], ext[1]):
				if nomesalva[0][-3:] == ext[1]:
					nomesalva = nomesalva[0]
				else:
					nomesalva = nomesalva[0] + '.' + ext[1]
				# salva os dados de fato
				try:
					salvar.to_excel(nomesalva)
					QtWidgets.QMessageBox.information(self, 'Concluído!', 'Relatório salvo com sucesso.')
				except ImportError:
					QtWidgets.QMessageBox.critical(self, 'Erro ao salvar', 'Instale a biblioteca <b>python3-xlwt</b>!')
					
		else:
			QtWidgets.QMessageBox.critical(self, 'Erro', 'Faça alguma operação primeiro!')
	
	def checarextensao(self):
		if self.xls_rb.isChecked(): return
		if self.html_rb.isChecked(): return ['Arquivo HTML', 'html']
		if self.txt_rb.isChecked(): return ['Arquivo de Texto', 'txt']
		
	def atualizalabelspizza(self, b, lb, p, lp, i, o):
		self.ben_lb.setText('%s %%' % b)
		self.pben_lb.setText('%s %%' % lb)
		self.pat_lb.setText('%s %%' % p)
		self.ppat_lb.setText('%s %%' % lp)
		self.inc_lb.setText('%s %%' % i)
		self.out_lb.setText('%s %%' % o)
		self.pie_gv.setScene(self.piechart(b, lb, p, lp, i, o))
		
	def piechart(self, pben, plben, ppat, plpat, punc, poth):
		# cria elemento de cena para o gráfico de pizza
		cena = QtWidgets.QGraphicsScene()
		
		# define vetor com os valores das porcentagens
		# 'Benígno', 'Provavelmente benígno', 'Patogênico', 'Provavelmente patogênico', 'Incerto'
		valores = [pben, plben, ppat, plpat, punc, poth]
		total = sum(valores)
		
		# define as cores (verde, verde leve, vermelho, vermelho leve, cinza)
		cores = list(map(QColor,['#33cc33', '#70db70', '#ff3300', '#ff704d', '#669999', '#8c8c8c']))
		
		# parâmetros para definir a elipse
		angulo_i = 0
		contador = 0
		
		# desenha cada fatia da elipse
		for v in valores:
			# Max span is 5760, so we have to calculate corresponding span angle
			angulo = round(float(v * 5760) / total)
			elipse = QtWidgets.QGraphicsEllipseItem(0, 0, 200, 200)
			elipse.setPos(0, 0)
			elipse.setStartAngle(angulo_i)
			elipse.setSpanAngle(angulo)
			elipse.setBrush(cores[contador])
			angulo_i += angulo
			contador += 1
			cena.addItem(elipse)
		return cena
	
# ################## #
# inicia a aplicação #
# ################## #

application = QtWidgets.QApplication(sys.argv)
Window = DNAContultVariantReport_GUI(None)
Window.show()
application.exec_()
