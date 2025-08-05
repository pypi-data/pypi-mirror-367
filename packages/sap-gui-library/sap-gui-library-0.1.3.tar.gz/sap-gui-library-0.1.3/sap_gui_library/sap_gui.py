# Importing sleep to pause the execution of the code for a specified duration
from time import sleep

# Importing subprocess to run new applications or programs through the Python code
import subprocess

# Importing Literal to define a type with a specific set of possible string values
from typing import Literal,Union

# Importing pywintypes to handle Windows-specific data types and errors, often used with COM objects
import pywintypes

# Importing win32com.client to interact with COM objects and automation servers, such as Excel or SAP GUI
import win32com.client

# Importing json to work with JSON data, including parsing and generating JSON
import json

# Importing math to perform mathematical operations and functions, such as ceil
import math

# Importing pandas as pd to work with data structures, primarily DataFrames, for data manipulation and analysis
import pandas as pd

# Importing os to interact with the operating system, such as file and directory handling
import os

# Numerical computing with Python 
import numpy as np


class SapGui():

	"Inicia la interaccion con SAPGUI para usar la api de scripting"
	
	def __init__(
		self,
		path_logon:str = r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe",
		rest_time: float =0.5,
		conection:Literal["PRODUCTIVO","CALIDAD"]="PRODUCTIVO",
		user: str  = "",
		password: str ="",
		client: str = "400",
		lenguage: Literal["EN","ES"]="ES",
		option_multiple_logons:Literal[
			"1", #Continue with this logon and end any other logons in the system.
			"2", #Continue with this logon, without ending any other logons in the system.
			"3", #Terminate this logon
			] = "2",
		active: bool= False
		):

		"""
		# Parametros
		-------
		- path_logon: The file path to the SAP Logon executable. Defaults to the standard installation path.
		- rest_time: The delay time (in seconds) between steps in the logon process. Default is 0.5 seconds.
		- conection: The type of SAP connection to use.Default is "PRODUCTIVO".
		- user: The SAP username. Default is an empty string.
		- password: The SAP password. Default is an empty string.
		- client: The SAP client number. Default is "400".
		- lenguage: The language for the SAP session. "EN" for English, "ES" for Spanish. Default is "ES".
		- option_multiple_logons: The action to take if multiple logons are detected "1" - Continue with this logon and end any other logons in the system. "2" - Continue with this logon, without ending any other logons in the system. "3" - Terminate this logon Default is "2",
		- active: Select the SAP logon detected
		"""

		if active:

			self.sap_gui_auto = win32com.client.GetObject("SAPGUI")   
			self.application = self.sap_gui_auto.GetScriptingEngine
			self.connection = self.application.Children(0) ####validar este punto
			self.session = self.connection.Children(0)
			
		else:

			path = path_logon
			subprocess.Popen(path)
			sleep(rest_time)

			# try three times open the conection
			for i in range(0,3):
				try:
					self.sap_gui_auto = win32com.client.GetObject("SAPGUI")   
					self.application = self.sap_gui_auto.GetScriptingEngine
					break
				except Exception as e:
					print("ERROR: Unable to connect to SAPGUI")
					sleep(rest_time)
					if i==2:
						raise Exception

			try:
				self.connection = self.application.OpenConnection(conection, True)
				self.session = self.connection.Children(0)
			except pywintypes.com_error as e:
				print(f"ERROR: Unable to connect to '{conection}'")
				sleep(rest_time)
				return

			# Mandante
			self.session.findById("wnd[0]/usr/txtRSYST-MANDT").Text = client
			# User
			self.session.findById("wnd[0]/usr/txtRSYST-BNAME").Text = user
			# Password
			self.session.findById("wnd[0]/usr/pwdRSYST-BCODE").Text = password
			# Lenguage
			self.session.findById("wnd[0]/usr/txtRSYST-LANGU").Text = lenguage
			# Enter
			self.session.findById("wnd[0]").sendVkey(0)

			alert=1
			while int(self.session.Children.Count)>1:
				sleep(rest_time)
				title_alert=self.session.Children.Item(alert).Text
				
				#windows of information
				if title_alert == "Información" or title_alert == "Information":
					self.session.findById("wnd[1]/tbar[0]/btn[0]").Press()

				#windows of copyright
				if title_alert=="Copyright":
					self.session.findById("wnd[1]/tbar[0]/btn[0]").Press()
				
				#windows of multiple sessions
				elif "License" in title_alert or "licencia" in title_alert:
					radio_buttons={
						"1":"wnd[1]/usr/radMULTI_LOGON_OPT1",
						"2":"wnd[1]/usr/radMULTI_LOGON_OPT2",
						"3":"wnd[1]/usr/radMULTI_LOGON_OPT3"
					}
					for key, value in radio_buttons.items():
						if key == option_multiple_logons:
							# Aquí estamos comparando la clave con el valor_a_comparar
							if self.session.findById(value, False) is not None:
								self.session.findById(value, False).Select()
								self.session.findById("wnd[1]/tbar[0]/btn[0]").press()

	def get_session(self):
		"""Returns the current SAP session"""
		return self.connection.Children(0)
	
	def get_connection(self):
		"""Returns the current SAP connection"""
		return self.connection

	def close_sap(self):
		"""Closes the SAP session"""
		self.get_session().findById("wnd[0]/tbar[0]/okcd").Text = "/n"
		self.get_session().findById("wnd[0]").sendVKey(0)
		self.get_session().findById("wnd[0]").close()
		self.get_session().findById("wnd[1]/usr/btnSPOP-OPTION1").Press()

	def get_user(self):
		"""Return the session user"""
		return self.get_session().Info.User


class Transaction:
	"""Abstracción de las transacciones de sap en su uso más común"""
	def __init__(self, session, code: str):
		"""
		Parameters
		----------
		- session: object - Session with which the transaction will be initiated.
		- code: str - Name assigned to the transaction.
		"""
		self.session = session
		self.code = code

	def start_transaction(self):
		"""Starts the transaction using the provided session and code."""
		self.session.StartTransaction(self.code)

	def end_transaction(self):
		"""Ends the current transaction."""
		self.session.EndTransaction()

	def get_code_transaction(self) -> str:
		"""
		Retrieves the transaction code.

		Returns
		-------
		- str The current transaction code.
		"""
		return self.session.Info.Transaction

	def lock_session_ui(self):
		"""Locks the session UI to prevent user interaction."""
		self.session.LockSessionUI()

	def unlock_session_ui(self):
		"""Unlocks the session UI to allow user interaction."""
		self.session.UnlockSessionUI()

	def select_variant(
			self,
			variant_author: str = "",
			variant_name: str = "",
			variant_type: Literal["Click", "Author"] = "Author"):
		"""
		Selects the variant for a transaction.

		Parameters
		----------
		- variant_author: str, optional -	Author of the variant, if needed.
		- variant_name: str - Name of the variant.
		- variant_type: Literal["Click", "Author"], optional -- Specifies whether the variant box requires the user's name or if the variant should be selected by clicking. Default is "Author".
		"""
		self.session.findById("wnd[0]/tbar[1]/btn[17]").press()

		if variant_type == "Author":
			self.session.findById("wnd[1]/usr/txtENAME-LOW").text = variant_author
			self.session.findById("wnd[1]/usr/txtV-LOW").text = variant_name
			self.session.findById("wnd[1]/tbar[0]/btn[8]").press()
		else:
			variant_list = self.session.findById("wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell")
			for i in range(0, int(variant_list.RowCount)):
				try:
					variante = variant_list.GetCellValue(i, "VARIANT")
					if variante == variant_name:
						variant_list.selectedRows = f"{i}"
						variant_list.currentCellRow = f"{i}"
						variant_list.doubleClickCurrentCell()
						break
				except:
					pass

	def run_transaction(self, bttn: Literal["Execute", "Continue"] = "Execute"):
		"""
		Executes the action within the transaction.

		Parameters
		----------
		- bttn: Literal["Execute", "Continue"], optional -- Specifies how the transaction should be executed. Default is "Execute".
		"""
		if bttn == "Execute":
			self.session.findById("wnd[0]/tbar[1]/btn[8]").press()
		else:
			self.session.findById("wnd[0]/tbar[0]/btn[0]").press()

	def get_shell_id(self,dictionary:dict={}) -> str:
		"""
		Searches for the grid-shell ID currently on the screen.

		Returns
		-------
		- str - The grid-shell ID if found, otherwise None.
		"""
		if not dictionary:
			childrens = self.session.GetObjectTree("wnd[0]/usr")
			dictionary = json.loads(childrens)
		else:pass
			
			
		for key, value in dictionary.items():
			if isinstance(value, list):
				for item in value:
					result = self.get_shell_id(item)
					if result is not None:
						return result
			elif isinstance(value, dict):
				result = self.get_shell_id(value)
				if result is not None:
					return result
			elif key == 'Id':
				try:
					if self.session.findById(value).subtype == "GridView" or self.session.findById(value).type == "GridView":
						return str(value).replace("", "")
				except:
					pass

	def get_column_names(self, grid_id:str=None) -> list[str]:
		"""
		Retrieves the names of the columns from a grid ID.

		Parameters
		----------
		- grid_id: str - The grid view from which to obtain the column names.

		Returns
		-------
		- list[str] - A list of the column names.
		"""

		if grid_id==None:
			grid_view=self.session.findById(self.get_shell_id())
		else:
			grid_view = self.session.findById(grid_id)
			
		columns = grid_view.Columncount
		columns_names = []
		for j in range(0, columns):
			name_column = grid_view.GetColumnTitles(grid_view.ColumnOrder.Item(j))[0]
			columns_names.append(name_column)

		seen = {}
		new_columns = []
		
		for column in columns_names:
			if column not in seen:
				seen[column] = 1
				new_columns.append(column)
			else:
				new_name = f"{column}_{seen[column]}"
				new_columns.append(new_name)
				seen[column] += 1
				
		return new_columns

	def export_in_shell_or_grid(self,
			btn_id_expand: str = "&NAVIGATION_PROFILE_TOOLBAR_EXPAND",
			btn_id_export: str = "&MB_EXPORT",
			item_menu: str = "&PC"):
		"""
		Searches for the export button within the toolbar contained in the grid.

		Parameters
		----------
		- btn_id_expand: str, optional - Specifies if there is an expand button to locate the export button. Default is "&NAVIGATION_PROFILE_TOOLBAR_EXPAND".
		- btn_id_export: str, optional - The ID of the export button. Default is "&MB_EXPORT".
		- item_menu: str, optional - Menu item where "Fichero local..." or export option is found. Default is "&PC".
		"""
		grid_view = self.session.FindById(self.get_shell_id())
		try:
			grid_view.pressToolbarButton(btn_id_expand)
		except:
			pass
		sleep(0.7)
		grid_view.pressToolbarButton(btn_id_export)
		grid_view.selectContextMenuItem(item_menu)

	def export_in_toolbar(self, number_button: str):
		"""
		Presses the export button on the toolbar.

		Parameters
		----------
		- number_button: str - Number of the button to press, can be str or int.
		"""
		self.session.findById(f"wnd[0]/tbar[1]/btn[{number_button}]").press()

	def export_in_menu(self, step_to_export: list[int] = [0, 1, 2]):
		"""
		Option to export from the menu bar.

		Parameters
		----------
		- step_to_export: list[int], optional - Sequential list to navigate to the option that says "Fichero local..." or export option. Default is [0, 1, 2].
		"""
		base_id = "wnd[0]/mbar"
		
		for i, step in enumerate(step_to_export):
			base_id += f"/menu[{step}]"
		
		self.session.findById(base_id).select()

	def select_export_and_download(self,
			address: str,
			name: str,
			type_export: Literal["0", "1", "2"] = "1",
			encoding: str = "4310",
			selection: Literal["Create", "Replace", "Add"] = "Replace"):
		"""
		Controls the export window.

		Parameters
		----------
		- address: str - Specific path where the file will be exported.
		- name: str - Name of the file without extension.
		- type_export: Literal["0", "1", "2"], optional - Selects the type of file to create. Default is "1".

			>>> {"0":"Not converted", "1":"Tab-separated text", "2":"Rich text format"}

		- encoding: str, optional - Specifies the encoding of the file. Default is "4310".
		- selection: Literal["Create", "Replace", "Add"], optional - Controls whether to create, replace, or add to a file. Default is "Replace".
		"""
		self.session.findById(f"wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[{type_export},0]").select()
		self.session.findById(f"wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[{type_export},0]").setFocus()
		self.session.findById("wnd[1]/tbar[0]/btn[0]").press()

		if type_export in ["0", "1", "2"]:
			self.session.findById("wnd[1]/usr/ctxtDY_PATH").text = address
			self.session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = f"{name}.csv"
			self.session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").text = encoding

		if selection == "Create":
			self.session.findById("wnd[1]/tbar[0]/btn[0]").press()
		elif selection == "Replace":
			self.session.findById("wnd[1]/tbar[0]/btn[11]").press()
		elif selection == "Add":
			self.session.findById("wnd[1]/tbar[0]/btn[7]").press()

	def select_value_in_shell(self, shell_id: str, name_label: str = "", value_to_search: str = ""):
		"""
		Allows selecting a value from gridView type tables.

		Parameters
		----------
		- shell_id: str - The ID of the grid where the action will take place.
		- name_label: str, optional - The name of the field where the value will be searched. If you don't know how to find it, you need to select the column, click on the help button, then technical information, and you will see 'Field Name'. Default is an empty string.
		- value_to_search: str - The value to search in the specified column.

		"""
		find = False
		shell = self.session.findById(shell_id)
		for i in range(0, int(shell.RowCount)):
			try:
				shell.currentCellRow = i
				value = shell.GetCellValue(i, name_label)
				if value == value_to_search:
					shell.selectedRows = f"{i}"
					shell.doubleClickCurrentCell()
					find = True
					break
				else:
					continue
			except Exception as e:
				pass
		if not find:
			raise KeyError(f"The specified value '{value_to_search}' was not found.")

	def select_value_in_tables_type_label(self, container_id: str, column: int, value: str, virtual_key_page: int = 82, virtual_key_enter: int = 0):
		"""
		Allows selecting a value from label-type tables that can be accessed when selecting an option for a button.
		Remember to first open the selection menu where this function will operate.

		Parameters
		----------
		- container_id: str - The ID of the container where the list or all labels are located, usually "wnd[1]/usr/sub/1[0,0]/sub/1/2[0,0]" but can vary.
		- column: int - The column number where the value will be searched; remember that 0 = first column.
		- value: str - The value we are looking for, for example, in a display variant '000001'.
		- virtual_key_page: int, optional - The virtual key that will be sent to SAP to scroll through pages. Default is 82.
		- virtual_key_enter: int, optional - The virtual key that will be sent to SAP to select the value we are searching for. Default is 0.
		"""
		container = self.session.FindById(container_id)
		scrollbar = self.session.findById("wnd[1]/usr").verticalScrollbar
		cicle = math.ceil(scrollbar.Maximum / scrollbar.PageSize)
		win1 = self.session.findById("wnd[1]")

		find = False
		for i in range(cicle + 1):
			container = self.session.FindById("wnd[1]/usr/sub/1[0,0]/sub/1/2[0,0]")
			for child in container.children:
				if self.session.findById(child.id).type == "GuiSimpleContainer":
					rows = self.session.findById(child.id).children
					label = rows.ElementAt(column)
					cell = str(label.text).strip()

					if cell == value:
						label.setFocus()
						win1.SendVKey(virtual_key_enter)
						find = True
						return

			if not find:
				win1.SendVKey(virtual_key_page)
			else:
				return

		raise ValueError("The specified value was not found.")

	def set_values_in_multiple_selection(self, tab_name: Literal["Select values", "Exclude values"] = "Select values", actions: list[str] = ["Clear", "Paste", "Take"]):
		"""
		Performs the action of copying and pasting values in the multiple selection window.

		Parameters
		----------
		- tab_name: str, optional - The tab where the values will be pasted. Default is "Select values".
		- actions: list[str], optional - The respective actions to perform; the default is to clear the fields, paste values, and click the 'Take' button. Default is ["Clear", "Paste", "Take"].
		"""
		tabs = {
			"Select values": "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA",
			"Exclude values": "wnd[1]/usr/tabsTAB_STRIP/tabpNOSV",
		}
		buttons_toolbar = {
			"Take": "wnd[1]/tbar[0]/btn[8]",
			"Clear": "wnd[1]/tbar[0]/btn[16]",
			"Paste": "wnd[1]/tbar[0]/btn[24]",
		}
		self.session.findById(tabs[tab_name]).select()
		for action in actions:
			self.session.findById(buttons_toolbar[action]).press()

	def set_values_in_multiple_selection_file(self, df: pd.DataFrame, column: str, address: str, name: str, clean_before: bool = True, unique: bool = False, tab_name: Literal["Select values", "Exclude values"] = "Select values"):
		"""
		Performs the action of copying and pasting values from a file in the multiple selection window. This is done via a file to allow multiple bots to do it simultaneously without clipboard conflicts.

		Parameters
		----------
		- df: pd.DataFrame - The DataFrame being used.
		- column: str - The column containing the values to paste.
		- address: str - The path where the file will be saved.
		- name: str - The name of the file.
		- clean_before: bool, optional - Indicates whether to click the clear button to empty the current values. Default is True.
		- unique: bool, optional - Specifies whether to use unique values from the column. Default is False.
		- tab_name: str, optional - The tab where the values will be pasted. Default is "Select values".
		"""
		tabs = {
			"Select values": "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA",
			"Select intervals": "wnd[1]/usr/tabsTAB_STRIP/tabpINTL",
			"Exclude values": "wnd[1]/usr/tabsTAB_STRIP/tabpNOSV",
			"Exclude intervals": "wnd[1]/usr/tabsTAB_STRIP/tabpNOINT",
		}

		if unique:
			pd.Series(df[column].unique()).to_csv(os.path.join(address, f"{name}.txt"), header=False, index=False)
		else:
			df[column].to_csv(os.path.join(address, f"{name}.txt"), header=False, index=False)

		if tab_name:
			self.session.findById(tabs[tab_name]).select()

		if clean_before:
			self.session.findById("wnd[1]/tbar[0]/btn[16]").press()
		self.session.findById("wnd[1]/tbar[0]/btn[23]").press()
		self.session.findById("wnd[2]/usr/ctxtDY_PATH").text = address
		self.session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = f"{name}.txt"
		self.session.findById("wnd[2]/tbar[0]/btn[0]").press()
		self.session.findById("wnd[1]/tbar[0]/btn[8]").press()


class DataProcess():

	"""Proceso de etl de la información descargada de sap para su procesamiento"""

	def __init__(
			self,
			address_file,
			type_file:str ="csv",
			skiprows:Literal["0","3","6"]="3",
			encoding:Literal["utf-8","latin1"]="utf-8"):
		
		"""
		Allows for the processing of tables or sheets downloaded from SAP

		Parameters
		-------
		- address_file: Location address where the file is read
		- type_file: Type of file to be read ["csv", "html"] = "csv" by default, csv is used
		- skiprows: Specifies the number of rows to skip when reading a file

		Process
		-------
		- Identifies the file type for further handling or modification; in both cases, a basic transformation is applied using the received parameters

		"""

		self.type_file=type_file
		if self.type_file=="csv":
			self.df = pd.read_csv(
				address_file,
				sep='\t',
				lineterminator="\r",
				skiprows=int(skiprows),
				encoding=encoding,
				dtype=str,
				on_bad_lines='skip'
			)
		else:raise ValueError("No se a establecido otro tipo de lectura a archivos")

	def edit_file(self, 
			skip_first_row:bool=True,
			skip_last_row:bool=True, 
			strip_columns:Union[bool, int]=bool,
			dropna_columns:list=[], 
			columns_to_int:list=[],
			columns_to_str:list=[],
			columns_to_datetime:list=[],
			columns_from_str_to_float:list=[],
			columns_from_float_to_str:list=[], 
			columns_to_strip:list=[],
			generic_name_columns:list=[],
			select_columns: Union[list, int]=list,
			):
		
		"""
		Function responsible for editing, correcting, and applying data transformations to the file.

		Parameters
		----------
		* skip_first_row: After most of the corrective process, the first row often contains NaN values, so it is removed.
		* skip_last_row: After most of the corrective process, the last row often contains NaN values, so it is removed.
		* strip_columns: Indicates if columns should be stripped of whitespace (left and right).
		* dropna_columns: Specifies the columns where rows with missing values (NaN) should be dropped.
		* columns_to_int: Specifies the columns that will be converted to integer type.
		* columns_to_str: Specifies the columns that will be converted to string type.
		* columns_to_datetime: Specifies the columns that will be converted to datetime type.
		* columns_from_str_to_float: Specifies the columns of string type that will be converted to float type.
		* columns_from_float_to_str: Specifies the columns of float type that will be converted to string type.
		* columns_to_strip: Specifies the columns where leading and trailing whitespace will be removed.
		* generic_name_columns: Specifies the columns that will be assigned a generic name.
		* select_columns: Specifies which columns to select from the entire dataframe. Can accept either column names or column indices.

		Process
		-------
		* Cleans and purifies the dataframe according to the parameters provided.
		The process is designed so that the user always assigns generic names to columns, and based on those names, the respective transformations and corrections are applied.
		"""

		# Eliminar columnas vacías
		self.df = self.deletecolumns(df=self.df)

		if strip_columns==True:self.df.columns = self.df.columns.str.strip()
		# Renombre columnas
		if generic_name_columns:self.df.rename(columns=dict(zip(self.df.columns, generic_name_columns)), inplace=True)

		# Eliminar la primera fila si es solicitado
		if skip_first_row: self.df = self.df.iloc[1:].reset_index(drop=True)
		if skip_last_row: 
			if isinstance(skip_last_row,bool):
				self.df = self.df.iloc[:self.df.shape[0] - 1].reset_index(drop=True)
			elif isinstance(skip_last_row,int):
				self.df = self.df.iloc[:self.df.shape[0] - skip_last_row].reset_index(drop=True)
			else: raise ValueError("skip_last_row debe ser 'True' para borrar solo una  o 'int' para borrar cantidades")

		# Borrar columnas nan
		if dropna_columns:
			self.df.dropna(subset=dropna_columns, axis=0, inplace=True)

		self.df=self.df.reset_index(drop=True)

		# Convertir columnas a datetime
		if columns_to_datetime:
			self.df[columns_to_datetime] = self.df[columns_to_datetime].apply(pd.to_datetime, errors='coerce',dayfirst=True)


		# Convertir columnas a int
		for columna in columns_to_int:
			self.df[columna] = self.df[columna].apply(lambda x: self.to_int(x))

		# Convertir columnas a str
		self.df[columns_to_str] = self.df[columns_to_str].astype(str)

		# Convertir columnas desde float a str
		for column in columns_from_float_to_str:
			for i in range(len(self.df)):
				try:
					value = int(self.df.loc[i, column])
					self.df.loc[i, column] = str(value)
				except ValueError:pass
		self.df[columns_from_float_to_str] = self.df[columns_from_float_to_str].astype(str)

		# Strip las columnas necesarias
		for columna in columns_to_strip: self.df[columna] = self.df[columna].str.strip()

		# Columnas de string a numéricas
		for columna in columns_from_str_to_float:
			self.df[columna] = self.df[columna].apply(lambda x: self.fStr2float(x))
			self.df[columna] = pd.to_numeric(self.df[columna], errors='coerce')
		
		# Selecciona columnas que se desean ver según la posición o etiqueta
		if select_columns:
			if isinstance(select_columns[0], int): self.df = self.df.iloc[:, select_columns]
			else:self.df = self.df.loc[:, select_columns]

	def get_df(self):
		"""return df to use"""
		return self.df
		
	def save_file(self,address,name,like:Literal["Excel","csv"]="csv",index=False):

		"""
		Guarda el archivo

		Parametros
		-------
		* address: Dirección donde se guardará el archivo
		* name: Nombre con el cual será guardado el archivo, sin especificar extención
		* like: Especifica si el archivo es un excel o un csv
		* index: Especifica si quiere guardar el archivo con indices o no
		"""

		full_adress = os.path.join(address,  name) + (".txt" if like=="csv" else ".xlsx")
		if like=="csv": self.df.to_csv(full_adress,index=index)
		if like=="Excel": self.df.to_excel(full_adress,index=index)
		
	@staticmethod
	def deletecolumns(df:pd.DataFrame):
		"""Borra aquellas columnas que no son necesarias """
		for tittle in df.columns:
			tittle = str(tittle)
			if tittle == '\n' or tittle[0:3] == 'Unn' or tittle==' ': df = df.drop(tittle, axis=1)
		return(df)

	@staticmethod
	def fStr2float(x):
		"""Cambia el valor string a un float"""
		try:
			x = x.rstrip()
			x = x.lstrip()
			x = x.replace(",", "")
			if x[-1] == '-': negative = True
			else: negative = False 

			x = float(x)
			if negative: x *= -1 
			return x
		
		except: return x  
		
	@staticmethod
	def to_int(x):
		try:
			if pd.isna(x) or x==None or x == np.nan :return pd.NA
			x = (str(x).strip()).replace(",", "")
			if x[-1] == '-': negative = True
			else: negative = False 
			x = int(float(x))
			if negative: x *= -1 
			return x
		except: return x  
		