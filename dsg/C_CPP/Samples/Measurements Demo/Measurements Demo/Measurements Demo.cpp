// Measurements Demo.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include <math.h>
#include "..\..\..\ACSC.h"
#include "PreciseTimer.h"


// CHANGE THOSE SETTINGS ACCORDING TO NEEDED PERFORMANCE MEASUREMENTS
// ------------------------------------------------------------------
#define SHARED_MEMORY							// UNCOMMENT IF REQUIRED
#define READ_WRITE_VARIABLES_MEASUREMENTS		// UNCOMMENT IF REQUIRED
#define CALLBACKS_MEASUREMENTS					// UNCOMMENT IF REQUIRED
//#define TEST_MEASUREMENTS						// UNCOMMENT IF REQUIRED


typedef enum
{
	TCP_COMMUNICATION			= 1,
	UDP_COMMUNICATION			= 2,
	SIMULATOR_COMMUNICATION		= 3,
#if !defined(SHARED_MEMORY)
	SERIAL_COMMUNICATION,
	PCI_COMMUNICATION,
#endif
	REMOTE_COMMUNICATION,
	EXIT
} COMMUNICATION_TYPE;


// DEFINE NUMBER OF REQUIRED ITERATIONS
// ------------------------------------
const int n_iterations = 100;

unsigned __int64 read_write_variables_results[n_iterations];
unsigned __int64 callbacks_results[n_iterations];
unsigned int counter = 0;

#if defined(TEST_MEASUREMENTS)
	HANDLE CallbackReceivedEvent = NULL;
	bool isRunning = true;
#endif

CPreciseTimer preciseTimer;

#if defined(CALLBACKS_MEASUREMENTS)
	int WINAPI Callback_Motion64(UINT64 Param, void* UserParameter);
	int WINAPI Callback_Motor64(UINT64 Param, void* UserParameter);
	int WINAPI Callback_ProgramEx64(UINT64 Param, void* UserParameter);
	int WINAPI Callback_SystemError64(UINT64 Param, void* UserParameter);
	int WINAPI Callback_EtherCATError64(UINT64 Param, void* UserParameter);
	int WINAPI Callback_Emergency(UINT64 Param, void* UserParameter);
#endif

#if defined(CALLBACKS_MEASUREMENTS) || defined(TEST_MEASUREMENTS)
	int WINAPI Callback_Program64(UINT64 Param, void* UserParameter);
#endif

#if defined(TEST_MEASUREMENTS)
	int WINAPI Callback_ProgramEnd64(UINT64 Param, void* UserParameter);
#endif


void perform_statistics_calculations(unsigned __int64* results, int n_samples)
{
	// PRINT SOME STATISTICS
	unsigned __int64 min = results[0], max = results[0];
	double average = 0;
	for (int i = 0; i < n_samples; i++)
	{
		if (min > results[i])
			min = results[i];
		if (max < results[i])
			max = results[i];
		average += results[i];
	}
	average = (average / (double)n_samples);

	printf("\nStatistics over %d samples:\n", n_samples);
	printf("-----------------------------\n");
	printf("Minimum value: %I64u microseconds\n", min);
	printf("Maximum value: %I64u microseconds\n", max);
	printf("Average: %.2f microseconds\n", average);
	printf("\n");
}

int _tmain(int argc, _TCHAR* argv[])
{
	const static int NUMBER_OF_ROWS = 10;
	const static int NUMBER_OF_POINTS = 200;
	double* LONG_ARRAY_TO_WRITE = NULL;
	double* LONG_ARRAY_TO_READ = NULL;
	unsigned int NUMBER_OF_WRITTEN_POINTS = 0;
	
	unsigned int Address = 0;
	HANDLE hComm = ACSC_INVALID;
	int iterator = 0;
	int i = 0;

#if !defined(SHARED_MEMORY)
	ACSC_PCI_SLOT Cards[10];
	int ObtainedCards = 0;
	int PCISlot = -1;
	int COMPort = 0;
	int COMBaudRate = 115200;
#endif

	int Received = 0;
	int CommType = 0;
	char IPAddress[200];
	bool Connected = false;



	printf ("\n|******************************************************************|");
	printf ("\n|***                     SPiiPlus C Library                     ***|");
	printf ("\n|***                Performance Measurements Test               ***|");
	printf ("\n|***     Version 2.70 Copyright (C) ACS Motion Control 2019     ***|");
	printf ("\n|******************************************************************|\n");

   
	Received = (int)acsc_GetLibraryVersion();
	printf("SPiiPlus C Library version %d.%d.%d.%d\n", Received >> 24, (Received >> 16) & 0xFF, (Received >> 8) & 0xFF, Received & 0xFF);

#if !defined(SHARED_MEMORY)
	if (acsc_GetPCICards(Cards, 10, &ObtainedCards))
	{
		printf("SPiiPlus card found Bus %d, Slot %d, Function %d\n", Cards[0].BusNumber, Cards[0].SlotNumber, Cards[0].Function);
	}
#endif


	/////////////////////////////////////////////////////////////////////////////////////
	// OPEN COMMUNICATION
	/////////////////////////////////////////////////////////////////////////////////////
	do
	{
		printf("\n\nPlease select the communication type (1-5) that you want to test with:\n");
		printf("1. Press 1 for Ethernet Network (TCP) communication\n");
		printf("2. Press 2 for Ethernet Point-to-Point (UDP) communication\n");
		printf("3. Press 3 for Simulator communication\n");
#if !defined(SHARED_MEMORY)
		printf("4. Press 4 for Serial communication\n");
		printf("5. Press 5 for PCI communication\n");
		printf("6. Press 6 for establishing connection to remote PC\n");
		printf("7. Press 7 to Exit\n\n");
#else
		printf("4. Press 4 for establishing connection to remote PC\n");
		printf("5. Press 5 to Exit\n\n");
#endif

		scanf_s("%d", &CommType);
		if ((CommType < 0) || (CommType > 7))
		{
			printf("Wrong communication type !\n\n");
			continue;
		}
			
		switch (CommType)
		{
			case TCP_COMMUNICATION:
				printf("\nPlease enter IP address:");
				scanf_s("%s", IPAddress, _countof(IPAddress));
				printf("Trying to communicate using Ethernet Network (TCP) Communication (IP:%s) . . .\n", IPAddress);
				hComm = acsc_OpenCommEthernetTCP(IPAddress, ACSC_SOCKET_STREAM_PORT);
				if (hComm == ACSC_INVALID)
				{
					printf("acsc_OpenCommEthernetTCP(): Error while trying to open Ethernet Network (TCP) Communication: %d\n",
						acsc_GetLastError());
					continue;
				}
				Connected = true;
				break;

			case UDP_COMMUNICATION:
				printf("\nPlease enter IP address:");
				scanf_s("%s", IPAddress, _countof(IPAddress));
				printf("Trying to communicate using Ethernet Point-to-Point (UDP) Communication (IP:%s) . . .\n", IPAddress);
				hComm = acsc_OpenCommEthernetUDP(IPAddress, ACSC_SOCKET_DGRAM_PORT);
				if (hComm == ACSC_INVALID)
				{
					printf("acsc_OpenCommEthernetUDP(): Error while trying to open Ethernet Point-to-Point (UDP) Communication: %d\n",
						acsc_GetLastError());
					continue;
				}
				Connected = true;
				break;

			case SIMULATOR_COMMUNICATION:
				hComm = acsc_OpenCommSimulator();
				if (hComm == ACSC_INVALID)
				{
					printf("Cannot open direct simulator communication!\n");
					continue;
				}
				Connected = true;
				break;

#if !defined(SHARED_MEMORY)
			case SERIAL_COMMUNICATION:
				printf("\nPlease enter COM port number:");
				scanf_s("%d", COMPort, sizeof(int));
				printf("\nPlease enter COM baud rate number:");
				scanf_s("%d", COMBaudRate, sizeof(int));
				printf("Trying to communicate using Serial Communication (COM:%d, BAUD:%d) . . .\n", COMPort, COMBaudRate);
				hComm = acsc_OpenCommSerial(COMPort, COMBaudRate);
				if (hComm == ACSC_INVALID)
				{
					printf("acsc_OpenCommSerial(): Error while trying to open Serial Communication: %d\n",
						acsc_GetLastError());
					continue;
				}
				Connected = true;
				break;			

			case PCI_COMMUNICATION:
				printf("\nPlease enter PCI slot number:");
				scanf_s("%d", PCISlot, sizeof(int));
				hComm = acsc_OpenCommPCI(PCISlot);
				if (hComm == ACSC_INVALID)
				{
					printf("Cannot open PCI communication!\n");
					continue;
				}
				Connected = true;
				break;
#endif

			case REMOTE_COMMUNICATION:
				printf("\nPlease enter remote IP address:");
				scanf_s("%s", IPAddress, _countof(IPAddress));
				printf("Connecting to %s...", IPAddress);
			
				if( !acsc_SetServerExtLogin(IPAddress, 9999, NULL, NULL, NULL) )
				{
					printf("Cannot establish remote connection to %s..\n", IPAddress);
					continue;
				}
				else
				{
					printf("Remote connection established successfully.\n");
				}
				break;

			case EXIT:
				acsc_CloseComm(hComm);
				return 1;
				break;
		}
	} while (!Connected);

	printf("Communication was opened successfully.\n");
#if defined(_DEBUG)
	getchar();
#endif


#if defined(CALLBACKS_MEASUREMENTS)
	/////////////////////////////////////////////////////////////////////////////////////
	// SET CALLBACKS
	/////////////////////////////////////////////////////////////////////////////////////
#if defined(_DEBUG)
	printf("\nInitializing Callbacks . . .\n");
#endif

	//set callback for motion end
	if (!acsc_InstallCallback(hComm, Callback_Motion64, NULL/*&preciseTimer*/, ACSC_INTR_PHYSICAL_MOTION_END))
	{
		printf("acsc_InstallCallback(): ACSC_INTR_PHYSICAL_MOTION_END Callback Registration Error: %d\n", acsc_GetLastError());
		goto END;
	}

	//set callback for motor error
	if (!acsc_InstallCallback(hComm, Callback_Motor64, NULL/*&preciseTimer*/, ACSC_INTR_MOTOR_FAILURE))
	{
		printf("acsc_InstallCallback(): ACSC_INTR_MOTOR_FAILURE Callback Registration Error: %d\n", acsc_GetLastError());
		goto END;
	}

	//set callback for program interrupt_ex
	if (!acsc_InstallCallback(hComm, Callback_ProgramEx64, NULL, ACSC_INTR_ACSPL_PROGRAM_EX))
	{
		printf("acsc_InstallCallback(): ACSC_INTR_ACSPL_PROGRAM_EX Callback Registration Error: %d\n", acsc_GetLastError());
		goto END;
	}

	//set callback for program interrupt
	if (!acsc_InstallCallback(hComm, Callback_Program64, /*NULL*/&preciseTimer, ACSC_INTR_ACSPL_PROGRAM))
	{
		printf("acsc_InstallCallback(): ACSC_INTR_ACSPL_PROGRAM Callback Registration Error: %d\n", acsc_GetLastError());
		goto END;
	}

	//set callback for emergency stop
	if (!acsc_InstallCallback(hComm, Callback_Emergency, NULL, ACSC_INTR_EMERGENCY))
	{
		printf("acsc_InstallCallback(): ACSC_INTR_EMERGENCY Callback Registration Error: %d\n", acsc_GetLastError());
		goto END;
	}

	//set callback for EtherCAT error
	if (!acsc_InstallCallback(hComm, Callback_EtherCATError64, NULL, ACSC_INTR_ETHERCAT_ERROR))
	{
		printf("acsc_InstallCallback(): ACSC_INTR_ETHERCAT_ERROR Callback Registration Error: %d\n", acsc_GetLastError());
		goto END;
	}

	//set callback for system error
	if (!acsc_InstallCallback(hComm, Callback_SystemError64, NULL, ACSC_INTR_SYSTEM_ERROR))
	{
		printf("acsc_InstallCallback(): ACSC_INTR_SYSTEM_ERROR Callback Registration Error: %d\n", acsc_GetLastError());
		goto END;
	}

#if defined(_DEBUG)
	printf("Callbacks were initialized successfully, Press any key to continue . . .\n");
	getchar();
#endif
#endif

#if defined(TEST_MEASUREMENTS)
	//set callback for program end
	if (!acsc_InstallCallback(hComm, Callback_ProgramEnd64, NULL/*&preciseTimer*/, ACSC_INTR_PROGRAM_END))
	{
		printf("acsc_InstallCallback(): ACSC_INTR_PROGRAM_END Callback Registration Error: %d\n", acsc_GetLastError());
		goto END;
	}

	//set callback for program interrupt
//	if (!acsc_InstallCallback(hComm, Callback_Program64, /*NULL*/&preciseTimer, ACSC_INTR_ACSPL_PROGRAM))
//	{
//		printf("acsc_InstallCallback(): ACSC_INTR_ACSPL_PROGRAM Callback Registration Error: %d\n", acsc_GetLastError());
//		goto END;
//	}

#if defined(_DEBUG)
	printf("Callbacks were initialized successfully, Press any key to continue . . .\n");
	getchar();
#endif
#endif

	/////////////////////////////////////////////////////////////////////////////////////
	// LOAD D-BUFFER CONTENTS WITH VARIABLES DEFINITIONS
	/////////////////////////////////////////////////////////////////////////////////////
#if defined(_DEBUG)
	printf("\nLoading D-Buffer contents . . .\n");
#endif

#if defined(SHARED_MEMORY)
	char* d_buffer_contents = "!axisdef X=0,Y=1,Z=2,T=3,A=4,B=5,C=6,D=7\r\n						\
!axisdef x=0,y=1,z=2,t=3,a=4,b=5,c=6,d=7\r\n													\
global int I(100),I0,I1,I2,I3,I4,I5,I6,I7,I8,I9,I90,I91,I92,I93,I94,I95,I96,I97,I98,I99\r\n		\
global real V(100),V0,V1,V2,V3,V4,V5,V6,V7,V8,V9,V90,V91,V92,V93,V94,V95,V96,V97,V98,V99\r\n	\
global real shm MULTIDIM_LONG_ARRAY(10)(200)\r\n												\
global real shm LONG_ARRAY(200)\r\n																\
global real shm HELLO_VAR(2)(2)\r\n																\
global int shm SEMAPHORE\r\n";
#else
	char* d_buffer_contents = "!axisdef X=0,Y=1,Z=2,T=3,A=4,B=5,C=6,D=7\r\n						\
!axisdef x=0,y=1,z=2,t=3,a=4,b=5,c=6,d=7\r\n													\
global int I(100),I0,I1,I2,I3,I4,I5,I6,I7,I8,I9,I90,I91,I92,I93,I94,I95,I96,I97,I98,I99\r\n		\
global real V(100),V0,V1,V2,V3,V4,V5,V6,V7,V8,V9,V90,V91,V92,V93,V94,V95,V96,V97,V98,V99\r\n	\
global real TEST_PARAM(2)(2)\r\n																\
global int SEMAPHORE\r\n";
#endif

	char* d_buffer_index_query = "?sysinfo(11)\r";
	char* stop_and_reset_all_buffers = "##SR\r";
	char str[20] = {'\0'};
	int received = 0;
	unsigned int BufferIndex = 0;
	unsigned int DBufferIndex = 0;

	if (!acsc_Transaction(hComm, d_buffer_index_query, (int)strlen(d_buffer_index_query), str, (DWORD)(sizeof(str)), &received, NULL))
	{
		printf("acsc_Transaction(): Transaction Error During Getting D-Buffer index: %d\n", acsc_GetLastError());
		goto END;
	}
	if (!received)
	{
		printf("acsc_Transaction(): Transaction Error During Getting D-Buffer index: %d\n", acsc_GetLastError());
		goto END;
	}
	str[received - 1] = '\0';
	sscanf_s(str, "%d", &DBufferIndex);

	if (!acsc_Command(hComm, stop_and_reset_all_buffers, (int)strlen(stop_and_reset_all_buffers), NULL))
	{
		printf("acsc_Transaction(): Transaction Error During Stopping and Reset all buffers: %d\n", acsc_GetLastError());
		goto END;
	}

	if (!acsc_LoadBuffer(hComm, DBufferIndex, d_buffer_contents, (int)strlen(d_buffer_contents), NULL))
	{
		printf("acsc_LoadBuffer(): Transaction Error During Loading D-Buffer contents: %d\n", acsc_GetLastError());
		goto END;
	}

	if (!acsc_CompileBuffer(hComm, DBufferIndex, NULL))
	{
		printf("acsc_CompileBuffer(): Transaction Error During Compiling D-Buffer contents: %d\n", acsc_GetLastError());
		goto END;
	}

#if defined(_DEBUG)
	printf("D-Buffer contents were loaded successfully, Press any key to continue . . .\n");
	getchar();
#endif


#if defined(READ_WRITE_VARIABLES_MEASUREMENTS)
  #if defined(SHARED_MEMORY)
	/////////////////////////////////////////////////////////////////////////////////////
	// WRITE SHARED MEMORY (SINGLE VALUE)
	/////////////////////////////////////////////////////////////////////////////////////
	printf("\nWriting Single Value to Shared Memory . . .\n");
	double data[2][2] = { {1.112, 2.334}, {4.565, 7.456} };
	double read_data[2][2] = {0};

	Address = 0;
	if (!acsc_GetSharedMemoryAddress(hComm, ACSC_NONE, "HELLO_VAR", &Address, NULL))
	{
		printf("acsc_GetSharedMemoryAddress(): Transaction Error During Getting Shared Memory Variable Address: %d\n", acsc_GetLastError());
		goto END;
	}

	for (iterator = 0; iterator < n_iterations; iterator++)
	{
		// CLEAR PREVIOUS RESULT FIRST
		read_write_variables_results[iterator] = 0;

		// start the timer
		preciseTimer.StartTimer();

		if (!acsc_WriteSharedMemoryReal(hComm, Address, 0, 0, 0, 0, &(data[0][0])))
		{
			printf("acsc_WriteSharedMemoryReal(): Transaction Error During Writing Shared Memory Variable: %d\n", acsc_GetLastError());
			goto END;
		}

		// Stop the timer
		preciseTimer.StopTimer();

		if (!acsc_WriteSharedMemoryReal(hComm, Address, 0, 0, 1, 1, &(data[0][1])))
		{
			printf("acsc_WriteSharedMemoryReal(): Transaction Error During Writing Shared Memory Variable: %d\n", acsc_GetLastError());
			goto END;
		}
		if (!acsc_WriteSharedMemoryReal(hComm, Address, 1, 1, 0, 0, &(data[1][0])))
		{
			printf("acsc_WriteSharedMemoryReal(): Transaction Error During Writing Shared Memory Variable: %d\n", acsc_GetLastError());
			goto END;
		}
		if (!acsc_WriteSharedMemoryReal(hComm, Address, 1, 1, 1, 1, &(data[1][1])))
		{
			printf("acsc_WriteSharedMemoryReal(): Transaction Error During Writing Shared Memory Variable: %d\n", acsc_GetLastError());
			goto END;
		}

		read_write_variables_results[iterator] = preciseTimer.GetTime();
	}

	// PRINT SOME STATISTICS
	perform_statistics_calculations(read_write_variables_results, n_iterations);
	printf("Writing Single Value to Shared Memory was completed successfully\n");
	
#if defined(_DEBUG)
	printf("Press any key to continue . . .\n");
	getchar();
#endif


	/////////////////////////////////////////////////////////////////////////////////////
	// READ SHARED MEMORY (SINGLE VALUE)
	/////////////////////////////////////////////////////////////////////////////////////
	printf("\nReading Single Value from Shared Memory . . .\n");

	Address = 0;
	if (!acsc_GetSharedMemoryAddress(hComm, ACSC_NONE, "HELLO_VAR", &Address, NULL))
	{
		printf("acsc_GetSharedMemoryAddress(): Transaction Error During Getting Shared Memory Variable Address: %d\n", acsc_GetLastError());
		goto END;
	}

	for (iterator = 0; iterator < n_iterations; iterator++)
	{
		// CLEAR PREVIOUS RESULT FIRST
		read_write_variables_results[iterator] = 0;

		// start the timer
		preciseTimer.StartTimer();

		if (!acsc_ReadSharedMemoryReal(hComm, Address, 0, 0, 0, 0, &(read_data[0][0])))
		{
			printf("acsc_ReadSharedMemoryReal(): Transaction Error During Reading Shared Memory Variable: %d\n", acsc_GetLastError());
			goto END;
		}

		// Stop the timer
		preciseTimer.StopTimer();

		if (!acsc_ReadSharedMemoryReal(hComm, Address, 0, 0, 1, 1, &(read_data[0][1])))
		{
			printf("acsc_ReadSharedMemoryReal(): Transaction Error During Reading Shared Memory Variable: %d\n", acsc_GetLastError());
			goto END;
		}
		if (!acsc_ReadSharedMemoryReal(hComm, Address, 1, 1, 0, 0, &(read_data[1][0])))
		{
			printf("acsc_ReadSharedMemoryReal(): Transaction Error During Reading Shared Memory Variable: %d\n", acsc_GetLastError());
			goto END;
		}
		if (!acsc_ReadSharedMemoryReal(hComm, Address, 1, 1, 1, 1, &(read_data[1][1])))
		{
			printf("acsc_ReadSharedMemoryReal(): Transaction Error During Reading Shared Memory Variable: %d\n", acsc_GetLastError());
			goto END;
		}

		if ((data[0][0] != read_data[0][0]) || (data[0][1] != read_data[0][1]) ||
			(data[1][0] != read_data[1][0]) || (data[1][1] != read_data[1][1]))
		{
			printf("Error on reading - read data is not equal to written data.\n");
			goto END;
		}

		read_write_variables_results[iterator] = preciseTimer.GetTime();
	}

	// PRINT SOME STATISTICS
	perform_statistics_calculations(read_write_variables_results, n_iterations);
	printf("Reading Single Value from Shared Memory was completed successfully\n");
	
#if defined(_DEBUG)
	printf("Press any key to continue . . .\n");
	getchar();
#endif


	/////////////////////////////////////////////////////////////////////////////////////
	// WRITE SHARED MEMORY (ONE-DIMENSIONAL ARRAY of 200 VALUES)
	/////////////////////////////////////////////////////////////////////////////////////
	printf("\nWriting One-Dimensional Array of %d Values to Shared Memory . . .\n", NUMBER_OF_POINTS);

	// Initialize arrays
	if (LONG_ARRAY_TO_WRITE != NULL)
	{
		delete[] LONG_ARRAY_TO_WRITE;
		LONG_ARRAY_TO_WRITE = NULL;
	}
	if (LONG_ARRAY_TO_READ != NULL)
	{
		delete[] LONG_ARRAY_TO_READ;
		LONG_ARRAY_TO_READ = NULL;
	}
	LONG_ARRAY_TO_WRITE = new double[NUMBER_OF_POINTS];
	LONG_ARRAY_TO_READ = new double[NUMBER_OF_POINTS];

	int ONE_DIMENSIONAL_FACTOR = 100;

	Address = 0;
	if (!acsc_GetSharedMemoryAddress(hComm, ACSC_NONE, "LONG_ARRAY", &Address, NULL))
	{
		printf("acsc_GetSharedMemoryAddress(): Transaction Error During Getting Shared Memory Variable Address: %d\n", acsc_GetLastError());
		goto END;
	}

	for (iterator = 0; iterator < n_iterations; iterator++)
	{
		// CLEAR PREVIOUS RESULT FIRST
		read_write_variables_results[iterator] = 0;

		// INITIALIZE TESTING VALUES
		for (int INDEX = 0; INDEX < NUMBER_OF_POINTS; INDEX++)
		{
			LONG_ARRAY_TO_WRITE[INDEX] = ONE_DIMENSIONAL_FACTOR * cos(2*3.1415926/NUMBER_OF_POINTS*INDEX);
		}

		// start the timer
		preciseTimer.StartTimer();

		if (!acsc_WriteSharedMemoryReal(hComm, Address, 0, NUMBER_OF_POINTS - 1, ACSC_NONE, ACSC_NONE, LONG_ARRAY_TO_WRITE))
		{
			printf("acsc_WriteSharedMemoryReal(): Transaction Error During Writing Shared Memory Variable: %d\n", acsc_GetLastError());
			goto END;
		}

		// Stop the timer
		preciseTimer.StopTimer();

		// INCREMENT THE ONE_DIMENSIONAL_FACTOR - TO GET OTHER TESTING VALUES FOR NEXT TEST
		ONE_DIMENSIONAL_FACTOR++;

		read_write_variables_results[iterator] = preciseTimer.GetTime();
	}

	// PRINT SOME STATISTICS
	perform_statistics_calculations(read_write_variables_results, n_iterations);
	printf("Writing One-Dimensional Array of %d Values to Shared Memory was completed successfully\n", NUMBER_OF_POINTS);

#if defined(_DEBUG)
	printf("Press any key to continue . . .\n");
	getchar();
#endif


	/////////////////////////////////////////////////////////////////////////////////////
	// READ SHARED MEMORY (ONE-DIMENSIONAL ARRAY of 200 VALUES)
	/////////////////////////////////////////////////////////////////////////////////////
	printf("\nReading One-Dimensional Array of %d Values from Shared Memory . . .\n", NUMBER_OF_POINTS);

	Address = 0;
	if (!acsc_GetSharedMemoryAddress(hComm, ACSC_NONE, "LONG_ARRAY", &Address, NULL))
	{
		printf("acsc_GetSharedMemoryAddress(): Transaction Error During Getting Shared Memory Variable Address: %d\n", acsc_GetLastError());
		goto END;
	}

	for (iterator = 0; iterator < n_iterations; iterator++)
	{
		// CLEAR PREVIOUS RESULT FIRST
		read_write_variables_results[iterator] = 0;

		// start the timer
		preciseTimer.StartTimer();

		if (!acsc_ReadSharedMemoryReal(hComm, Address, 0, NUMBER_OF_POINTS - 1, ACSC_NONE, ACSC_NONE, LONG_ARRAY_TO_READ))
		{
			printf("acsc_ReadSharedMemoryReal(): Transaction Error During Reading Shared Memory Variable: %d\n", acsc_GetLastError());
			goto END;
		}

		// Stop the timer
		preciseTimer.StopTimer();

		for (int i = 0; i < NUMBER_OF_POINTS; i++)
		{
			if (LONG_ARRAY_TO_WRITE[i] != LONG_ARRAY_TO_READ[i])
			{
				printf("Error on reading - read data is not equal to written data.\n");
				goto END;
			}
		}

		read_write_variables_results[iterator] = preciseTimer.GetTime();
	}

	// PRINT SOME STATISTICS
	perform_statistics_calculations(read_write_variables_results, n_iterations);
	printf("Reading One-Dimensional Array of %d Values from Shared Memory was completed successfully AND COMPARED TO ORIGINAL DATA\n", NUMBER_OF_POINTS);
	
#if defined(_DEBUG)
	printf("Press any key to continue . . .\n");
	getchar();
#endif
	
	
	/////////////////////////////////////////////////////////////////////////////////////
	// WRITE SHARED MEMORY (TWO-DIMENTIONAL ARRAY of 10x200 VALUES)
	/////////////////////////////////////////////////////////////////////////////////////
	printf("\nWriting Two-Dimensional Array of %dx%d Values to Shared Memory . . .\n", NUMBER_OF_ROWS, NUMBER_OF_POINTS);

	// Initialize arrays
	LONG_ARRAY_TO_WRITE = new double[NUMBER_OF_ROWS * NUMBER_OF_POINTS];
	LONG_ARRAY_TO_READ = new double[NUMBER_OF_ROWS * NUMBER_OF_POINTS];

	int TWO_DIMENSIONAL_FACTOR = 100;

	Address = 0;
	if (!acsc_GetSharedMemoryAddress(hComm, ACSC_NONE, "MULTIDIM_LONG_ARRAY", &Address, NULL))
	{
		printf("acsc_GetSharedMemoryAddress(): Transaction Error During Getting Shared Memory Variable Address: %d\n", acsc_GetLastError());
		goto END;
	}

	for (iterator = 0; iterator < n_iterations; iterator++)
	{
		// CLEAR PREVIOUS RESULT FIRST
		read_write_variables_results[iterator] = 0;

		for (int INDEX1 = 0; INDEX1 < NUMBER_OF_ROWS; INDEX1++)
		{
			for (int INDEX2 = 0; INDEX2 < NUMBER_OF_POINTS; INDEX2++)
			{
				LONG_ARRAY_TO_WRITE[INDEX1 * NUMBER_OF_POINTS + INDEX2] = TWO_DIMENSIONAL_FACTOR * cos(2*3.1415926/NUMBER_OF_POINTS*(INDEX1+INDEX2));
			}
		}

		// start the timer
		preciseTimer.StartTimer();

		for (int INDEX1 = 0; INDEX1 < NUMBER_OF_ROWS; INDEX1++)
		{
			if (!acsc_WriteSharedMemoryReal(hComm, Address, INDEX1, INDEX1, 0, NUMBER_OF_POINTS - 1, &(LONG_ARRAY_TO_WRITE[INDEX1 * NUMBER_OF_POINTS])))
			{
				printf("acsc_WriteSharedMemoryReal(): Transaction Error During Writing Shared Memory Variable: %d\n", acsc_GetLastError());
				goto END;
			}
		}

		// Stop the timer
		preciseTimer.StopTimer();
	
		// INCREMENT THE ONE_DIMENSIONAL_FACTOR - TO GET OTHER TESTING VALUES FOR NEXT TEST
		TWO_DIMENSIONAL_FACTOR++;

		read_write_variables_results[iterator] = preciseTimer.GetTime();
	}

	// PRINT SOME STATISTICS
	perform_statistics_calculations(read_write_variables_results, n_iterations);
	printf("Writing Two-Dimensional Array of %dx%d Values to Shared Memory was completed successfully\n", NUMBER_OF_ROWS, NUMBER_OF_POINTS);
	
#if defined(_DEBUG)
	printf("Press any key to continue . . .\n");
	getchar();
#endif


	/////////////////////////////////////////////////////////////////////////////////////
	// READ SHARED MEMORY (TWO-DIMENTIONAL ARRAY OF 10x200 VALUES)
	/////////////////////////////////////////////////////////////////////////////////////
	printf("\nReading Two-Dimensional Array of %dx%d Values from Shared Memory . . .\n", NUMBER_OF_ROWS, NUMBER_OF_POINTS);

	Address = 0;
	if (!acsc_GetSharedMemoryAddress(hComm, ACSC_NONE, "MULTIDIM_LONG_ARRAY", &Address, NULL))
	{
		printf("acsc_GetSharedMemoryAddress(): Transaction Error During Getting Shared Memory Variable Address: %d\n", acsc_GetLastError());
		goto END;
	}

	for (iterator = 0; iterator < n_iterations; iterator++)
	{
		// CLEAR PREVIOUS RESULT FIRST
		read_write_variables_results[iterator] = 0;

		// start the timer
		preciseTimer.StartTimer();

		for (int INDEX1 = 0; INDEX1 < NUMBER_OF_ROWS; INDEX1++)
		{
			if (!acsc_ReadSharedMemoryReal(hComm, Address, INDEX1, INDEX1, 0, NUMBER_OF_POINTS - 1, &(LONG_ARRAY_TO_READ[INDEX1 * NUMBER_OF_POINTS])))
			{
				printf("acsc_ReadSharedMemoryReal(): Transaction Error During Reading Shared Memory Variable: %d\n", acsc_GetLastError());
				goto END;
			}
		}

		// Stop the timer
		preciseTimer.StopTimer();

		for (int i = 0; i < NUMBER_OF_POINTS; i++)
		{
			if (LONG_ARRAY_TO_WRITE[i] != LONG_ARRAY_TO_READ[i])
			{
				printf("Error on reading - read data is not equal to written data.\n");
				goto END;
			}
		}

		read_write_variables_results[iterator] = preciseTimer.GetTime();
	}

	// PRINT SOME STATISTICS
	perform_statistics_calculations(read_write_variables_results, n_iterations);
	printf("Reading Two-Dimensional Array of %dx%d Values from Shared Memory was completed successfully AND COMPARED TO ORIGINAL DATA\n", NUMBER_OF_ROWS, NUMBER_OF_POINTS);
	
#if defined(_DEBUG)
	printf("Press any key to continue . . .\n");
	getchar();
#endif

  #else // SHARED_MEMORY

	/////////////////////////////////////////////////////////////////////////////////////
	// WRITE PARAMETER
	/////////////////////////////////////////////////////////////////////////////////////
	printf("\nWriting Parameter . . .\n");
	double data[2][2] = { {1.112, 2.334}, {4.565, 7.456} };
	double read_data[2][2] = {0};

	for (iterator = 0; iterator < n_iterations; iterator++)
	{
		// CLEAR PREVIOUS RESULT FIRST
		read_write_variables_results[iterator] = 0;

		// start the timer
		preciseTimer.StartTimer();

		if (!acsc_WriteReal(hComm, ACSC_NONE, "TEST_PARAM", 0, 0, 0, 0, &(data[0][0]), NULL))
		{
			printf("acsc_WriteReal(): Transaction Error During Writing Parameter: %d\n", acsc_GetLastError());
			goto END;
		}

		// Stop the timer
		preciseTimer.StopTimer();

		read_write_variables_results[iterator] = preciseTimer.GetTime();
	}

	// PRINT SOME STATISTICS
	perform_statistics_calculations(read_write_variables_results, n_iterations);
	printf("Writing Parameter was completed successfully\n");
	
#if defined(_DEBUG)
	printf("Press any key to continue . . .\n");
	getchar();
#endif


	/////////////////////////////////////////////////////////////////////////////////////
	// READ PARAMETER
	/////////////////////////////////////////////////////////////////////////////////////
	printf("\nReading Parameter . . .\n");

	for (iterator = 0; iterator < n_iterations; iterator++)
	{
		// CLEAR PREVIOUS RESULT FIRST
		read_write_variables_results[iterator] = 0;

		// start the timer
		preciseTimer.StartTimer();

		if (!acsc_ReadReal(hComm, ACSC_NONE, "TEST_PARAM", 0, 0, 0, 0, &(read_data[0][0]), NULL))
		{
			printf("acsc_ReadReal(): Transaction Error During Reading Parameter: %d\n", acsc_GetLastError());
			goto END;
		}

		// Stop the timer
		preciseTimer.StopTimer();

		read_write_variables_results[iterator] = preciseTimer.GetTime();
	}

	// PRINT SOME STATISTICS
	perform_statistics_calculations(read_write_variables_results, n_iterations);
	printf("Reading Parameter was completed successfully\n");
	
#if defined(_DEBUG)
	printf("Press any key to continue . . .\n");
	getchar();
#endif

  #endif // SHARED_MEMORY
#endif // READ_WRITE_VARIABLES_MEASUREMENTS


#if defined(CALLBACKS_MEASUREMENTS)
	/////////////////////////////////////////////////////////////////////////////////////
	// LOAD BUFFER 1 CONTENTS FOR TESTING "INTERRUPT" / "INTERRUPTEX" CALLBACKS MECHANISM
	/////////////////////////////////////////////////////////////////////////////////////
	BufferIndex = 1;
	printf("\nLoading Buffer %d contents . . .\n", BufferIndex);

//	char* buffer_1_contents = "GG: IF(SEMAPHORE); interrupt; SEMAPHORE = 0; end; goto GG; stop";
	char* buffer_1_contents = "GG: IF(SEMAPHORE); interruptex(0x359, 0x9137); SEMAPHORE = 0; end; goto GG; stop";

	if (!acsc_StopBuffer(hComm, BufferIndex, NULL))
	{
		printf("acsc_StopBuffer(): Transaction Error During Stopping Buffer %d: %d\n", BufferIndex, acsc_GetLastError());
		goto END;
	}

	if (!acsc_LoadBuffer(hComm, BufferIndex, buffer_1_contents, (int)strlen(buffer_1_contents), NULL))
	{
		printf("acsc_LoadBuffer(): Transaction Error During Loading Buffer %d contents: %d\n", BufferIndex, acsc_GetLastError());
		goto END;
	}

	if (!acsc_CompileBuffer(hComm, BufferIndex, NULL))
	{
		printf("acsc_CompileBuffer(): Transaction Error During Compiling Buffer %d contents: %d\n", BufferIndex, acsc_GetLastError());
		goto END;
	}

	if (!acsc_RunBuffer(hComm, BufferIndex, NULL, NULL))
	{
		printf("acsc_RunBuffer(): Transaction Error During Running Buffer %d contents: %d\n", BufferIndex, acsc_GetLastError());
		goto END;
	}

#if defined(_DEBUG)
	printf("Buffer %d contents were loaded successfully, Press any key to continue . . .\n", BufferIndex);
	getchar();
#endif


	/////////////////////////////////////////////////////////////////////////////////////
	// START MOTION AND MEASUREMENTS
	/////////////////////////////////////////////////////////////////////////////////////
	printf("\nStarting Motion and Measurements . . .\n");
	int SEMAPHORE = 1;

	for (i = 0; i < n_iterations; i++)
	{
		callbacks_results[i] = 0;
	}

#if defined(SHARED_MEMORY)
	Address = 0;
	if (!acsc_GetSharedMemoryAddress(hComm, ACSC_NONE, "SEMAPHORE", &Address, NULL))
	{
		printf("acsc_GetSharedMemoryAddress(): Transaction Error During Getting Shared Memory Variable Address: %d\n", acsc_GetLastError());
		goto END;
	}
#endif

	for (i = 0; i < n_iterations; i++)
	{
		printf("Iteration %d of %d:\n", (i + 1), n_iterations);

		// start the timer
		preciseTimer.StartTimer();

#if defined(SHARED_MEMORY)
		if (!acsc_WriteSharedMemoryInteger(hComm, Address, ACSC_NONE, ACSC_NONE, ACSC_NONE, ACSC_NONE, &SEMAPHORE))
		{
			printf("acsc_WriteSharedMemoryReal(): Transaction Error During Writing Shared Memory Variable: %d\n", acsc_GetLastError());
			goto END;
		}
#else
		if (!acsc_WriteInteger(hComm, ACSC_NONE, "SEMAPHORE", ACSC_NONE, ACSC_NONE, ACSC_NONE, ACSC_NONE, &SEMAPHORE, NULL))
		{
			printf("acsc_WriteInteger(): Transaction Error During Writing Integer Variable: %d\n", acsc_GetLastError());
			goto END;
		}
#endif

		// TIMER WILL BE STOPPED BY RECEIVED CALLBACK - THE TIME WILL BE MEASURED THERE
		Sleep(1000);
	}

	Sleep(2000);

	// PRINT SOME STATISTICS
	perform_statistics_calculations(callbacks_results, n_iterations);

	getchar();
#endif

#if defined(TEST_MEASUREMENTS)
	/////////////////////////////////////////////////////////////////////////////////////
	// LOAD BUFFER 2 CONTENTS FOR TESTING "INTERRUPT" / "INTERRUPTEX" CALLBACKS MECHANISM
	/////////////////////////////////////////////////////////////////////////////////////
	BufferIndex = 2;
	printf("\nLoading Buffer %d contents . . .\n", BufferIndex);

//	char* buffer_2_contents = "interrupt;\nstop\n";
	char* buffer_2_contents = "global int count\ncount = count + 1\nstop\n";

	if (!acsc_StopBuffer(hComm, BufferIndex, NULL))
	{
		printf("acsc_StopBuffer(): Transaction Error During Stopping Buffer %d: %d\n", BufferIndex, acsc_GetLastError());
		goto END;
	}

	if (!acsc_LoadBuffer(hComm, BufferIndex, buffer_2_contents, (int)strlen(buffer_2_contents), NULL))
	{
		printf("acsc_LoadBuffer(): Transaction Error During Loading Buffer %d contents: %d\n", BufferIndex, acsc_GetLastError());
		goto END;
	}

	if (!acsc_CompileBuffer(hComm, BufferIndex, NULL))
	{
		printf("acsc_CompileBuffer(): Transaction Error During Compiling Buffer %d contents: %d\n", BufferIndex, acsc_GetLastError());
		goto END;
	}

#if defined(_DEBUG)
	printf("Buffer %d contents were loaded successfully, Press any key to continue . . .\n", BufferIndex);
	getchar();
#endif


	/////////////////////////////////////////////////////////////////////////////////////
	// START MEASUREMENTS
	/////////////////////////////////////////////////////////////////////////////////////
	printf("\nStarting Measurements . . .");

	for (i = 0; i < n_iterations; i++)
	{
		callbacks_results[i] = 0;
	}

	double startTime = 0, endTime = 0, timeElapsed = 0;

	CallbackReceivedEvent = CreateEvent(NULL, false, false, NULL);

	acsc_Command(hComm, "count = 0\r", 10, NULL);

	acsc_ReadReal(hComm, ACSC_NONE, "TIME", ACSC_NONE, ACSC_NONE, ACSC_NONE, ACSC_NONE, &startTime, NULL);

	while (isRunning)
	{
		// start the timer
		preciseTimer.StartTimer();

		if (!acsc_RunBuffer(hComm, BufferIndex, NULL, ACSC_IGNORE))
		{
			printf("acsc_RunBuffer(): Transaction Error During Running Buffer %d contents: %d\n", BufferIndex, acsc_GetLastError());
			goto END;
		}

		int r = WaitForSingleObject(CallbackReceivedEvent, INFINITE);
		if (r != WAIT_OBJECT_0)
			printf("WaitForSingleObject(): Error\n");
	}

	acsc_ReadReal(hComm, ACSC_NONE, "TIME", ACSC_NONE, ACSC_NONE, ACSC_NONE, ACSC_NONE, &endTime, NULL);

	timeElapsed = endTime - startTime;

	if (CallbackReceivedEvent != NULL)
	{
		CloseHandle(CallbackReceivedEvent);
		CallbackReceivedEvent = NULL;
	}

	printf("Done\n\n");
	printf("Number of runs: %d\nTime Elapsed = %f msec\n\n", counter, timeElapsed);

	// PRINT SOME STATISTICS
	perform_statistics_calculations(callbacks_results, n_iterations);

	getchar();
#endif

	// AN EXAMPLE FOR HOW TO MEASURE TIME TO START MOVEMENT IN ACSPL+
	// --------------------------------------------------------------
	//int start_time, end_time, total_time 
	//start_time = TIME; enable 0; till MST(0).#ENABLED; end_time = TIME; total_time = end_time - start_time; disp "TOTAL TIME FOR ENABLE MOTOR = %d", total_time
	//!start_time = TIME; ptp/r (0), 10000; till MST(0).#MOVE; end_time = TIME; total_time = end_time - start_time; disp "TOTAL TIME FOR START MOVEMENT = %d", total_time
	//start_time = TIME; ptp/r (0), 10000; till ^GPHASE(0); end_time = TIME; total_time = end_time - start_time; disp "TOTAL TIME FOR START MOVEMENT = %d", total_time
	//!GG: disp "GPHASE(0) = %d", GPHASE(0); if GPHASE(0) > 0 goto GG; end
	//stop


END:
	if (hComm != ACSC_INVALID)
	{
#if defined(CALLBACKS_MEASUREMENTS)
		//unset callback for motion end
		if (!acsc_InstallCallback(hComm, NULL, NULL, ACSC_INTR_PHYSICAL_MOTION_END))
		{
			printf("acsc_InstallCallback(): ACSC_INTR_PHYSICAL_MOTION_END Callback Unregistration Error: %d\n", acsc_GetLastError());
		}

		//unset callback for motor error
		if (!acsc_InstallCallback(hComm, NULL, NULL, ACSC_INTR_MOTOR_FAILURE))
		{
			printf("acsc_InstallCallback(): ACSC_INTR_MOTOR_FAILURE Callback Unregistration Error: %d\n", acsc_GetLastError());
		}

		//unset callback for program interrupt_ex
		if (!acsc_InstallCallback(hComm, NULL, NULL, ACSC_INTR_ACSPL_PROGRAM_EX))
		{
			printf("acsc_InstallCallback(): ACSC_INTR_ACSPL_PROGRAM_EX Callback Unregistration Error: %d\n", acsc_GetLastError());
		}

		//unset callback for program interrupt
		if (!acsc_InstallCallback(hComm, NULL, NULL, ACSC_INTR_ACSPL_PROGRAM))
		{
			printf("acsc_InstallCallback(): ACSC_INTR_ACSPL_PROGRAM Callback Unregistration Error: %d\n", acsc_GetLastError());
		}

		//unset callback for emergency stop
		if (!acsc_InstallCallback(hComm, NULL, NULL, ACSC_INTR_EMERGENCY))
		{
			printf("acsc_InstallCallback(): ACSC_INTR_EMERGENCY Callback Unregistration Error: %d\n", acsc_GetLastError());
		}

		//unset callback for EtherCAT error
		if (!acsc_InstallCallback(hComm, NULL, NULL, ACSC_INTR_ETHERCAT_ERROR))
		{
			printf("acsc_InstallCallback(): ACSC_INTR_ETHERCAT_ERROR Callback Unregistration Error: %d\n", acsc_GetLastError());
			goto END;
		}

		//unset callback for system error
		if (!acsc_InstallCallback(hComm, NULL, NULL, ACSC_INTR_SYSTEM_ERROR))
		{
			printf("acsc_InstallCallback(): ACSC_INTR_SYSTEM_ERROR Callback Unregistration Error: %d\n", acsc_GetLastError());
			goto END;
		}
#endif

#if defined(TEST_MEASUREMENTS)
		//unset callback for program end
		if (!acsc_InstallCallback(hComm, NULL, NULL/*&preciseTimer*/, ACSC_INTR_PROGRAM_END))
		{
			printf("acsc_InstallCallback(): ACSC_INTR_PROGRAM_END Callback Registration Error: %d\n", acsc_GetLastError());
		}

		//unset callback for program interrupt
//		if (!acsc_InstallCallback(hComm, NULL, NULL, ACSC_INTR_ACSPL_PROGRAM))
//		{
//			printf("acsc_InstallCallback(): ACSC_INTR_ACSPL_PROGRAM Callback Unregistration Error: %d\n", acsc_GetLastError());
//		}
#endif

		acsc_CloseComm(hComm);
		hComm = ACSC_INVALID;
	}

	if (LONG_ARRAY_TO_WRITE != NULL)
	{
		delete[] LONG_ARRAY_TO_WRITE;
		LONG_ARRAY_TO_WRITE = NULL;
	}

	if (LONG_ARRAY_TO_READ != NULL)
	{
		delete[] LONG_ARRAY_TO_READ;
		LONG_ARRAY_TO_READ = NULL;
	}

	printf("Press any key to exit . . .\n");
	getchar();

	return 0;
}


#if defined(CALLBACKS_MEASUREMENTS)
	int WINAPI Callback_Motion64(UINT64 Param, void* UserParameter)
	{
		printf("Callback_Motion64(): INTERRUPT_PHYSICAL_MOTION_END Callback received. (Parameter: %I64u)\n", Param);
		return 0;
	}

	int WINAPI Callback_Motor64(UINT64 Param, void* UserParameter)
	{
		printf("Callback_Motor64(): INTERRUPT_MOTOR_FAILURE Callback received. (Parameter: %I64u)\n", Param);
		return 0;
	}

	int WINAPI Callback_ProgramEx64(UINT64 Param, void* UserParameter)
	{
		// Stop the timer
		preciseTimer.StopTimer();

		// Measure the time
		unsigned __int64 i64Counter = preciseTimer.GetTime();
		if (counter < n_iterations)
		{
			callbacks_results[counter++] = i64Counter;
		}

		UINT Param1 = Param >> 32;
		UINT Param2 = Param & 0x00000000FFFFFFFF;

		printf("Callback_ProgramEx64(): ACSC_INTR_ACSPL_PROGRAM_EX Callback received (counter = %d). (Parameter 1: 0x%x, Parameter 2: 0x%x), Time = %I64d microseconds\n", counter, Param1, Param2, i64Counter);

		return 0;
	}

	int WINAPI Callback_SystemError64(UINT64 Param, void* UserParameter)
	{
		printf("Callback_SystemError64(): ACSC_INTR_SYSTEM_ERROR Callback received. (Parameter: %I64u)\n", Param);
		return 0;
	}

	int WINAPI Callback_EtherCATError64(UINT64 Param, void* UserParameter)
	{
		printf("Callback_EtherCATError64(): ACSC_INTR_ETHERCAT_ERROR Callback received. (Parameter: %I64u)\n", Param);
		return 0;
	}

	int WINAPI Callback_Emergency(UINT64 Param, void* UserParameter)
	{
		printf("Callback_Emergency(): ACSC_INTR_EMERGENCY Callback received. (Parameter: %I64u)\n", Param);
		return 0;
	}
#endif

#if defined(CALLBACKS_MEASUREMENTS) || defined(TEST_MEASUREMENTS)
	int WINAPI Callback_Program64(UINT64 Param, void* UserParameter)
	{
		// Stop the timer
		preciseTimer.StopTimer();

		// Measure the time
		unsigned __int64 i64Counter = preciseTimer.GetTime();
		if (counter < n_iterations)
		{
			callbacks_results[counter++] = i64Counter;
		}
		else
		{
#if defined(TEST_MEASUREMENTS)
			isRunning = false;
#endif
		}            

#if defined(TEST_MEASUREMENTS)
        if (CallbackReceivedEvent != NULL)
			SetEvent(CallbackReceivedEvent);
#endif

#if defined(CALLBACKS_MEASUREMENTS)
		printf("Callback_Program64(): INTERRUPT_ACSPL_PROGRAM Callback received (counter = %d). (Parameter: %I64u), Time = %I64d microseconds\n", counter, Param, i64Counter);
#endif

		return 0;
	}
#endif

#if defined(TEST_MEASUREMENTS)
	int WINAPI Callback_ProgramEnd64(UINT64 Param, void* UserParameter)
	{
		//printf("Callback_ProgramEnd64(): INTERRUPT_PROGRAM_END Callback received. (Parameter: %I64u)\n", Param);

		// Stop the timer
		preciseTimer.StopTimer();

		// Measure the time
		unsigned __int64 i64Counter = preciseTimer.GetTime();
		if (counter < n_iterations)
		{
			callbacks_results[counter++] = i64Counter;
		}
		else
		{
			isRunning = false;
		}            

		if (CallbackReceivedEvent != NULL)
			SetEvent(CallbackReceivedEvent);

		return 0;
	}
#endif