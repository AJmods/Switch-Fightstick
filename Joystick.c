/*
Nintendo Switch Fightstick - Proof-of-Concept

Based on the LUFA library's Low-Level Joystick Demo
	(C) Dean Camera
Based on the HORI's Pokken Tournament Pro Pad design
	(C) HORI

This project implements a modified version of HORI's Pokken Tournament Pro Pad
USB descriptors to allow for the creation of custom controllers for the
Nintendo Switch. This also works to a limited degree on the PS3.

Since System Update v3.0.0, the Nintendo Switch recognizes the Pokken
Tournament Pro Pad as a Pro Controller. Physical design limitations prevent
the Pokken Controller from functioning at the same level as the Pro
Controller. However, by default most of the descriptors are there, with the
exception of Home and Capture. Descriptor modification allows us to unlock
these buttons for our use.
*/

/** \file
 *
 *  Main source file for the posts printer demo. This file contains the main tasks of
 *  the demo and is responsible for the initial application hardware configuration.
 */

#include "Joystick.h"
#include "uart.h"

#define CPU_PRESCALE(n) (CLKPR = 0x80, CLKPR = (n))
#define BAUD_RATE 38400
#define true 1
#define false 0

extern const uint8_t image_data[0x12c1] PROGMEM;

//button states
//left stick
int l_moveLeft = false;
int l_moveRight = false;
int l_moveUp = false;
int l_moveDown = false;

//right stick
int r_moveLeft = false;
int r_moveRight = false;
int r_moveUp = false;
int r_moveDown = false;

//buttons
int aPressed = false;
int bPressed = false;
int yPressed = false;
int xPressed = false;
int lPressed = false;
int rPressed = false;
int zlPressed = false;
int zrPressed = false;
int plusPressed = false;
int minusPressed = false;
int homePressed = false;
int capturePressed = false;
int rStickPressed = false;
int lStickPressed = false;

//dpad
int dpadLeftPressed = false;
int dpadRightPressed = false;
int dpadUpPressed = false;
int dpadDownPressed = false;



// Main entry point.
int main(void) {
    // We'll start by performing hardware and peripheral setup.
    SetupHardware();
    // We'll then enable global interrupts for our use.
    GlobalInterruptEnable();
    // Once that's done, we'll enter an infinite loop.
    uart_init(BAUD_RATE);
    for (;;)
    {
        // We need to run our task to process and deliver data for our IN and OUT endpoints.
        HID_Task();
        // We also need to run the main USB management task.
        USB_USBTask();
    }
}

// Configures hardware and peripherals, such as the USB peripherals.
void SetupHardware(void) {
    // We need to disable watchdog if enabled by bootloader/fuses.
    MCUSR &= ~(1 << WDRF);
    wdt_disable();

    // We need to disable clock division before initializing the USB hardware.
    clock_prescale_set(clock_div_1);
    // We can then initialize our hardware and peripherals, including the USB stack.

#ifdef ALERT_WHEN_DONE
    // Both PORTD and PORTB will be used for the optional LED flashing and buzzer.
	#warning LED and Buzzer functionality enabled. All pins on both PORTB and \
PORTD will toggle when printing is done.
	DDRD  = 0xFF; //Teensy uses PORTD
	PORTD =  0x0;
                  //We'll just flash all pins on both ports since the UNO R3
	DDRB  = 0xFF; //uses PORTB. Micro can use either or, but both give us 2 LEDs
	PORTB =  0x0; //The ATmega328P on the UNO will be resetting, so unplug it?
#endif
    // The USB stack should be initialized last.
    USB_Init();
}

// Fired to indicate that the device is enumerating.
void EVENT_USB_Device_Connect(void) {
    // We can indicate that we're enumerating here (via status LEDs, sound, etc.).
}

// Fired to indicate that the device is no longer connected to a host.
void EVENT_USB_Device_Disconnect(void) {
    // We can indicate that our device is not ready (via status LEDs, sound, etc.).
}

// Fired when the host set the current configuration of the USB device after enumeration.
void EVENT_USB_Device_ConfigurationChanged(void) {
    bool ConfigSuccess = true;

    // We setup the HID report endpoints.
    ConfigSuccess &= Endpoint_ConfigureEndpoint(JOYSTICK_OUT_EPADDR, EP_TYPE_INTERRUPT, JOYSTICK_EPSIZE, 1);
    ConfigSuccess &= Endpoint_ConfigureEndpoint(JOYSTICK_IN_EPADDR, EP_TYPE_INTERRUPT, JOYSTICK_EPSIZE, 1);

    // We can read ConfigSuccess to indicate a success or failure at this point.
}

// Process control requests sent to the device from the USB host.
void EVENT_USB_Device_ControlRequest(void) {
    // We can handle two control requests: a GetReport and a SetReport.

    // Not used here, it looks like we don't receive control request from the Switch.
}

// Process and deliver data from IN and OUT endpoints.
void HID_Task(void) {
    // If the device isn't connected and properly configured, we can't do anything here.
    if (USB_DeviceState != DEVICE_STATE_Configured)
        return;

    // We'll start with the OUT endpoint.
    Endpoint_SelectEndpoint(JOYSTICK_OUT_EPADDR);
    // We'll check to see if we received something on the OUT endpoint.
    if (Endpoint_IsOUTReceived())
    {
        // If we did, and the packet has data, we'll react to it.
        if (Endpoint_IsReadWriteAllowed())
        {
            // We'll create a place to store our data received from the host.
            USB_JoystickReport_Output_t JoystickOutputData;
            // We'll then take in that data, setting it up in our storage.
            while(Endpoint_Read_Stream_LE(&JoystickOutputData, sizeof(JoystickOutputData), NULL) != ENDPOINT_RWSTREAM_NoError);
            // At this point, we can react to this data.

            // However, since we're not doing anything with this data, we abandon it.
        }
        // Regardless of whether we reacted to the data, we acknowledge an OUT packet on this endpoint.
        Endpoint_ClearOUT();
    }

    // We'll then move on to the IN endpoint.
    Endpoint_SelectEndpoint(JOYSTICK_IN_EPADDR);
    // We first check to see if the host is ready to accept data.
    if (Endpoint_IsINReady())
    {
        // We'll create an empty report.
        USB_JoystickReport_Input_t JoystickInputData;
        // We'll then populate this report with what we want to send to the host.
        GetNextReport(&JoystickInputData);
        // Once populated, we can output this data to the host. We do this by first writing the data to the control stream.
        while(Endpoint_Write_Stream_LE(&JoystickInputData, sizeof(JoystickInputData), NULL) != ENDPOINT_RWSTREAM_NoError);
        // We then send an IN packet on this endpoint.
        Endpoint_ClearIN();
    }
}

typedef enum {
    SYNC_CONTROLLER,
    SYNC_POSITION,
    DONE,
    WAITING,
    HODL,
    UPDATE,
    CONNECT
} State_t;
State_t state = SYNC_CONTROLLER;

#define ECHOES 2
int echoes = 0;
USB_JoystickReport_Input_t last_report;
char c;
int report_count = 0;
int xpos = 0;
int ypos = 0;
int portsval = 0;

// Prepare the next report for the host.
void GetNextReport(USB_JoystickReport_Input_t* const ReportData) {

    // Prepare an empty report
    memset(ReportData, 0, sizeof(USB_JoystickReport_Input_t));
    ReportData->LX = STICK_CENTER;
    ReportData->LY = STICK_CENTER;
    ReportData->RX = STICK_CENTER;
    ReportData->RY = STICK_CENTER;
    ReportData->HAT = HAT_CENTER;

    // Repeat ECHOES times the last report
    if (echoes > 0)
    {
        memcpy(ReportData, &last_report, sizeof(USB_JoystickReport_Input_t));
        echoes--;
        return;
    }

    // States and moves management
    switch (state)
    {

        //SYNC_CONTROLLER is only called when Arduino is plugged in
        case SYNC_CONTROLLER:
            if (report_count > 100)
            {
                report_count = 0;
                state = UPDATE;
            }
            else if (report_count == 25 || report_count == 50)
            {
                ReportData->Button |= SWITCH_L | SWITCH_R;
            }
            else if (report_count == 75 || report_count == 100)
            {
                ReportData->Button |= SWITCH_A;
            }
            report_count++;
            break;

        case CONNECT:
            ReportData->Button |= SWITCH_L;
            ReportData->Button |= SWITCH_R;
            _delay_ms(500);
            state = UPDATE;
            break;
        case WAITING:
            state = UPDATE;
            break;
        case HODL:
            _delay_ms(5);
            state=UPDATE;
            break;
        case UPDATE:
            //---------------------------------------------------------------------------------------------------------------------------
            //Read UART char
            //---------------------------------------------------------------------------------------------------------------------------

            //Upper case is pressed, lowercase is released.
            c = uart_getchar();
            //TODO: convert to switch statement
            switch (c) {
                case 'U':
                    l_moveUp = true;
                    l_moveDown = false;
                    break;
                case 'u':
                    l_moveUp = false;
		                l_moveDown = false;
                    break;
                case 'D':
                    l_moveDown = true;
                    l_moveUp = false;
                    break;
                case 'd':
                    l_moveDown = false;
		                l_moveUp = false;
                    break;
                case 'L':
                    l_moveLeft = true;
                    l_moveRight = false;
                    break;
                case 'l':
                    l_moveLeft = false;
		                l_moveRight = false;
                    break;
                case 'R':
                    l_moveRight = true;
                    l_moveLeft = false;
                    break;
                case 'r':
                    l_moveRight = false;
		                l_moveLeft = false;
                    break;
                case 'I':
                    r_moveUp = true;
                    r_moveDown = false;
                    break;
                case 'i':
                    r_moveUp = false;
		                r_moveDown = false;
                    break;
                case 'K':
                    r_moveDown = true;
                    r_moveUp = false;
                    break;
                case 'k':
                    r_moveDown = false;
		                r_moveUp = false;
                    break;
                case 'J':
                    r_moveLeft = true;
                    r_moveRight = false;
                    break;
                case 'j':
                    r_moveLeft = false;
		                r_moveRight = false;
                    break;
                case 'M':
                    r_moveRight = true;
                    r_moveLeft = false;
                    break;
                case 'm':
                    r_moveRight = false;
		                r_moveLeft = false;
                    break;
                case 'A':
                    aPressed = true;
                    break;
                case 'a':
                    aPressed = false;
                    break;
                case 'B':
                    bPressed = true;
                    break;
                case 'b':
                    bPressed = false;
                    break;
                case 'Y':
                    yPressed = true;
                    break;
                case 'y':
                    yPressed = false;
                    break;
                case 'X':
                    xPressed = true;
                    break;
                case 'x':
                    xPressed = false;
                    break;
                case 'T':
                    lPressed = true;
                    break;
                case 't':
                    lPressed = false;
                    break;
                case 'W':
                    rPressed = true;
                    break;
                case 'w':
                    rPressed = false;
                    break;
                case 'F':
                    zlPressed = true;
                    break;
                case 'f':
                    zlPressed = false;
                    break;
                case 'G':
                    zrPressed = true;
                    break;
                case 'g':
                    zrPressed = false;
                    break;
                case 'O':
                    lStickPressed = true;
                    break;
                case 'o':
                    lStickPressed = false;
                    break;
                case 'P':
                    rStickPressed = true;
                    break;
                case 'p':
                    rStickPressed = false;
                case '+':
                    plusPressed = true;
                    break;
                case '=':
                    plusPressed = false;
                    break;
                case '-':
                    minusPressed = true;
                    break;
                case '_':
                    minusPressed = false;
                    break;
                case 'H':
                    homePressed = true;
                    break;
                case 'h':
                    homePressed = false;
                    break;
                case 'V':
                    capturePressed = true;
                    break;
                case 'v':
                    capturePressed = false;
                    break;
                case 'Q':
                    lStickPressed = true;
                    break;
                case 'q':
                    lStickPressed = false;
                    break;
                case 'E':
                    rStickPressed = true;
                    break;
                case 'e':
                    rStickPressed = false;
                    break;
                case 'C':
                    state = CONNECT;
                    break;
                case 'c':
                    state = CONNECT;
                    break;
            }

            //---------------------------------------------------------------------------------------------------------------------------
            //Button Actions
            //---------------------------------------------------------------------------------------------------------------------------

            //move left, right, or no direction among X axis.
            if (l_moveRight) {
                ReportData->LX = STICK_MAX;
            } else if (l_moveLeft) {
                ReportData->LX = STICK_MIN;
            } else { //This statement is probably not needed
                ReportData->LX = STICK_CENTER;
            }

            //move up, down, or no direction among Y axis.  Is inverted
            if (l_moveUp) {
                ReportData->LY = STICK_MIN;
            } else if (l_moveDown) {
                ReportData->LY = STICK_MAX;
            } else { //This statement is probably not needed
                ReportData->LY = STICK_CENTER;
            }
            if (r_moveRight) {
                ReportData->RX = STICK_MAX;
            } else if (r_moveLeft) {
                ReportData->RX = STICK_MIN;
            } else { //This statement is probably not needed
                ReportData->RX = STICK_CENTER;
            }

            //move up, down, or no direction among Y axis.  Is inverted
            if (r_moveUp) {
                ReportData->RY = STICK_MIN;
            } else if (r_moveDown) {
                ReportData->RY = STICK_MAX;
            } else { //This statement is probably not needed
                ReportData->RY = STICK_CENTER;
            }

            //check other buttons
            if (aPressed) {
                ReportData -> Button |= SWITCH_A;
            }
            if (bPressed) {
                ReportData -> Button |= SWITCH_B;
            }
            if (yPressed) {
                ReportData -> Button |= SWITCH_Y;
            }
            if (xPressed) {
                ReportData -> Button |= SWITCH_X;
            }
            if (lPressed) {
                ReportData -> Button |= SWITCH_L;
            }
            if (rPressed) {
                ReportData->Button |= SWITCH_R;
            }
            if (zlPressed) {
                ReportData->Button |= SWITCH_ZL;
            }
            if (zrPressed) {
                ReportData->Button |= SWITCH_ZR;
            }
            if (plusPressed) {
                ReportData -> Button |= SWITCH_PLUS;
            }
            if (minusPressed) {
                ReportData -> Button |= SWITCH_MINUS;
            }
            if (homePressed) {
                ReportData -> Button |= SWITCH_HOME;
            }
            if (capturePressed) {
                ReportData -> Button |= SWITCH_CAPTURE;
            }
            if (rStickPressed) {
                ReportData -> Button |= SWITCH_RCLICK;
            }
            if (lStickPressed) {
                ReportData -> Button |= SWITCH_LCLICK;
            }
            break;
        case DONE:
#ifdef ALERT_WHEN_DONE
            portsval = ~portsval;
			PORTD = portsval; //flash LED(s) and sound buzzer if attached
			PORTB = portsval;
			_delay_ms(250);
#endif
            return;

    }
    //inking

    // Prepare to echo this report
    memcpy(&last_report, ReportData, sizeof(USB_JoystickReport_Input_t));
    echoes = ECHOES;

}
