class GenericDataSaver:



	def __init__(  self
	
				 , main_save_path: str

				 , local_path: str

				 , path_suffix: str 

				 , DefaultValue: int = "0"

				 ) -> None:
		"""
:class:`DataSaver` is used to save and load data to and from a file. Designed for single file saving only.

If you need to save multiple files, create multiple instances with different paths.


:param main_save_path: The main directory where the save files will be stored. You can use "~/" to refer to the user's home directory.
	Example: "~/Documents/StudioName". Should be a valid path. Do not end with just "/", "\", or "~".

:param local_path: The subdirectory within the main save path where the save files will be stored.
	Example: "GameName/" or "GameName". Should NOT start with a "/" or a "\\" (if it does, it will be automatically stripped). Use only relative paths here.
	If a leading slash or backslash is present, it will be removed automatically.

:param path_suffix: The suffix for the save file, which will be appended to the local path.
	Example: "savefile.txt". Should not start with a "/" or a "\\". Recommended to use a file extension like ".txt" for compatibility.

:param DefaultValue: The default value to use if the save file is empty or does not exist.
	Should be a string representation, like "0" or "1,2,3".

:type main_save_path: str
:type local_path: str
:type path_suffix: str
:type DefaultValue: str
:return: None

.. note::
	This class is designed to be used in a Python environment where the `os` module is available.

.. warning::
	This class is not thread-safe. Use a lock in a multi-threaded environment.

Example usage:
	>>> DataSaver(main_save_path="~/Documents/DataSaver", local_path="DeleteMe", path_suffix="testfile.py.txt", DefaultValue="0")
	# If you pass local_path with a leading slash, e.g. "/DeleteMe/", it will be automatically corrected to "DeleteMe/".

:author: Nguyen Hoang Quoc Anh
:github: monbuticloud
"""
		
		import os
		self.os = os
		import base64
		self.base64 = base64
		
		print("DataSaver initialized")
		self.save_data = []


		# Normalize and join paths for cross-platform compatibility
		self.MainSavePath = self.os.path.expanduser(main_save_path)
		# Strip leading slashes and backslashes from local_path to prevent absolute path issues
		safe_local_path = local_path.lstrip("/\\")
		self.LocalPath = self.os.path.join(self.MainSavePath, safe_local_path)
		self.PathSuffix = path_suffix
		self.DefaultValue = DefaultValue
		

 










 

	def setup_paths(self, user):
		"""
		Set up the save and local directories. If a username is provided, it will be prepended to the path suffix.

		:param user: The username to append to the path suffix. If not provided, the default path suffix will be used.
		:type user: str
		:return: None

		Note: This will create the directories if they do not exist. Uses os.makedirs for cross-platform compatibility.
		"""
		print(self)
		if user:
			PathSuffix = f"{user}_{self.PathSuffix}"
		else:
			PathSuffix = self.PathSuffix
		self.PathSuffix = PathSuffix
		print("running os commands")
		# Use os.makedirs for cross-platform directory creation
		if not self.os.path.exists(self.MainSavePath):
			self.os.makedirs(self.MainSavePath, exist_ok=True)
		if not self.os.path.exists(self.LocalPath):
			self.os.makedirs(self.LocalPath, exist_ok=True)
		print("os commands done")






	def _Load(self) -> list[int]:
		"""
		Load data from the save file.

		:return: A list of integers loaded from the save file. If the file is empty or does not exist, it returns the default value as a list of integers.
		"""
		#Load save data
		##Savefile check
		save_data = []
		savefile_path = self.os.path.join(self.LocalPath, self.PathSuffix)
		if not self.os.path.exists(savefile_path):
			print("first run, creating save file")
			# Create the file using open for cross-platform compatibility
			with open(savefile_path, 'w', encoding='utf-8') as f:
				f.write("")
			save_string = self.DefaultValue
			print("created save file")
		##Read Savefile
		else:
			try:

				fd = self.os.open(savefile_path, self.os.O_CREAT | self.os.O_RDONLY)
				save_bytes = self.os.read(fd, 65536)
				try:
					save_string: str = (self.base64.b64decode(save_bytes)).decode()
				except Exception:
					save_string = ""
				print(f"read {len(save_string)}({save_string}) bytes from {savefile_path}")
				self.os.close(fd)
			except OSError as e:
				print(f"Error_SAVINGFUNCIN: {e}")
				print("Error reading save file: "+self.LocalPath+self.PathSuffix)
				assert False

		##Parse save data
		##Should not happen, but if the file is empty, set default value
		if save_string == "":
			save_string = self.DefaultValue  ##Default values if the file is empty

		
		print(save_string)

		save_data_str = save_string.split(",")
		for i in save_data_str:
			if i == "":
				i = 0
			save_data.append(int(i))
		return save_data




	def _Save(self,save_data: list) -> None:
		"""
		Save a list of integers to the save file.

		:param save_data: A list of integers to save to the file.
		:type save_data: list
		:return: None
		"""
		#Compile list

		save_data_str = []
		for i in save_data:
			save_data_str.append(str(i))

		save_string = ",".join(save_data_str)
		

		#Save data
		savefile_path = self.os.path.join(self.LocalPath, self.PathSuffix)
		try:
			fd = self.os.open(savefile_path, self.os.O_CREAT | self.os.O_WRONLY | self.os.O_TRUNC)
			print("Saving data to file...")
			bytes_written = self.os.write(fd, self.base64.b64encode(save_string.encode()))
			print(f'Wrote {bytes_written}({save_string}) bytes to "{savefile_path}".')
			self.os.close(fd)
			print("Data saved successfully.")
		except OSError as e:
			print(f"Error: {e}")
			print("Failed to save data.")
		finally:
			print("file closed")
	def _string_encode(self,s):
		return int.from_bytes(s.encode('utf-8')+ b'\x01','little')
	def _string_decode(self,i):
		recoveredbytes = int(i).to_bytes((int(i).bit_length() + 7) // 8, 'little')
		recoveredstring = recoveredbytes[:-1].decode('utf-8') # Strip pad before decoding
		return recoveredstring
	def Save(self, save_data):
		"""
		Public method to save a list of data (int, str, or bool) to the save file. Handles serialization.

		:param save_data: List of data to save (int, str, or bool values).
		:type save_data: list
		:return: None
		"""
		sterilizedSaveData = []
		for i in save_data:
			if type(i) == int:
				sterilizedSaveData.append(int("984911559"+str(i)))
			elif type(i) == str:
				if i=="True":
					i = "\\"+i
				elif i=="False":
					i = "\\"+i
				sterilizedSaveData.append(self._string_encode(i))
			elif type(i) == bool:
				if i:
					sterilizedSaveData.append(self._string_encode("True"))
				else:
					sterilizedSaveData.append(self._string_encode("False"))
		self._Save(sterilizedSaveData)
	def Load(self):
		"""
		Public method to load and deserialize data from the save file.

		:return: List of data (int, str, or bool values) loaded from the save file.
		"""
		sterilizedSaveData: list = self._Load()
		SaveData = []
		for i in sterilizedSaveData:
			i = str(i)
			if len(i) > 9:
				if i[:9] == "984911559":
					SaveData.append(int(i[9:]))
					continue
			i = int(i)
			i = self._string_decode(i)
			if i == "True":
				SaveData.append(True)
				continue
			if i == "False":
				SaveData.append(False)
				continue
			if i == "\\False":
				SaveData.append("False")
				continue
			if i == "\\True":
				SaveData.append("True")
				continue
			SaveData.append(i)
		return SaveData

			


			
		#984911559

	def __Test(self) -> None:
		
		print("WARNING: This is a test function. It will overwrite the save file with test data.")
		print("This function is not intended for production use. Use at your own risk.")
		print("Beginning Test... Please Control-C to exit or close the window to exit. if not, press enter to start the test.\n\n")
		_ = input()
		DataSave = GenericDataSaver(
			main_save_path="~/Documents/DataSaver",
			local_path="/DeleteMe/",
			path_suffix="testfile.py.txt",
			DefaultValue="0"
		)
		import random
		success = True
		DataSave.setup_paths("")
		print("Paths set up successfully.")
		print("Running number test...")
		for x in range(100):
			DataSave.Save([x, x+1, x+2, x+3, x+4, x+5, x+6, x+7, x+8, x+9])
			loaded_data = DataSave.Load()
			print("Loaded data:", loaded_data)
			if loaded_data == [x, x+1, x+2, x+3, x+4, x+5, x+6, x+7, x+8, x+9]:
				print("Test passed successfully!")
			else:
				print("Test failed. Loaded data does not match saved data.")
				success = False
		print("Running random data test...")
		print("This will save random data to the file and then load it back.")
		for x in range(10000):

			i = []
			for _ in range(100):
				i.append((random.randint(0, 16777216)))
			print(f"Saving random data interation: {x}")
			DataSave.Save(i)
			loaded_data = DataSave.Load()
			print("Loaded data:", loaded_data)
			if loaded_data == i:
				print("Test passed successfully!")
			else:
				success = False
				print("Test failed. Loaded data does not match saved data.")
		for x in range(100):

			i = []
			for _ in range(1000):
				i.append((random.randint(0, 2)))
			print(f"Saving random data interation: {x}")
			DataSave.Save(i)
			loaded_data = DataSave.Load()
			print("Loaded data:", loaded_data)
			if loaded_data == i:
				print("Test passed successfully!")
			else:
				success = False
				print("Test failed. Loaded data does not match saved data.")
		experimental_success = True
		print("Running experimental test...")
		for x in range(10000):
			name = str(random.randint(0, 1000000))+".txt"
			DataSave = GenericDataSaver(
				main_save_path="~/Documents/DataSaver",
				local_path="/DeleteMe/",
				path_suffix=name,
				DefaultValue="0"
			)
			DataSave.setup_paths("")
			print("Paths set up successfully.")
			i = []
			for _ in range(100):
				i.append((random.randint(0, 1)))
			print(f"Saving random data interation: {x}")
			DataSave.Save(i)
			loaded_data = DataSave.Load()
			print("Loaded data:", loaded_data)
			if loaded_data == i:
				print("Test passed successfully!")
			else:
				success = False
				print("Test failed. Loaded data does not match saved data.")
		if success:
			print("All tests passed successfully!")
		else:
			print("Some tests failed. Please check the output for details.")
		if experimental_success:
			print("Experimental tests passed successfully!")
		else:
			print("Some experimental tests failed. Please check the output for details.")
		print("Test completed. DataSaver is ready for use.")
		print("You can now use DataSaver to save and load data.")
		print("Test completed.")
		print("Exiting test.")

if __name__ == "__main__":
	print("DataSaver module is not meant to be run directly.")
	print("Please import it into your main application.")
	DataSave= GenericDataSaver(
		main_save_path="~/Documents/DataSaver",
		local_path="/DeleteMe/",
		path_suffix="testfile.py.txt",
		DefaultValue="0"
	)
	DataSave.setup_paths("")
	DataSave._GenericDataSaver__Test()
	print("Test completed. Exiting.")
	del DataSave
	print("DataSaver module has been cleaned up.")
	print("note that this is not supposed to be used normally, it is just a test file. please delete it after testing. please delete ~/Documents/DataSaver")
	exit(0)