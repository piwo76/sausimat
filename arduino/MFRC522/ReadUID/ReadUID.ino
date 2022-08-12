/**
 * --------------------------------------------------------------------------------------------------------------------
 * Example sketch/program showing how to read data from more than one PICC to serial.
 * --------------------------------------------------------------------------------------------------------------------
 * This is a MFRC522 library example; for further details and other examples see: https://github.com/miguelbalboa/rfid
 *
 * Example sketch/program showing how to read data from more than one PICC (that is: a RFID Tag or Card) using a
 * MFRC522 based RFID Reader on the Arduino SPI interface.
 *
 * Warning: This may not work! Multiple devices at one SPI are difficult and cause many trouble!! Engineering skill
 *          and knowledge are required!
 *
 * @license Released into the public domain.
 *
 * Typical pin layout used:
 * -----------------------------------------------------------------------------------------
 *             MFRC522      Arduino       Arduino   Arduino    Arduino          Arduino
 *             Reader/PCD   Uno/101       Mega      Nano v3    Leonardo/Micro   Pro Micro
 * Signal      Pin          Pin           Pin       Pin        Pin              Pin
 * -----------------------------------------------------------------------------------------
 * RST/Reset   RST          9             5         D9         RESET/ICSP-5     RST
 * SPI SS 1    SDA(SS)      ** custom, take a unused pin, only HIGH/LOW required **
 * SPI SS 2    SDA(SS)      ** custom, take a unused pin, only HIGH/LOW required **
 * SPI MOSI    MOSI         11 / ICSP-4   51        D11        ICSP-4           16
 * SPI MISO    MISO         12 / ICSP-1   50        D12        ICSP-1           14
 * SPI SCK     SCK          13 / ICSP-3   52        D13        ICSP-3           15
 *
 * More pin layouts for other boards can be found here: https://github.com/miguelbalboa/rfid#pin-layout
 *
 */

#include <SPI.h>
#include <MFRC522.h>
#include <Keypad.h>

#define SS_PIN 10
#define RST_PIN 2
#define NUMROWS 1
#define NUMCOLS 3
#define LONGPRESSINTERVAL_MS 3000

byte buttons[NUMROWS][NUMCOLS] = {
    {0, 1, 2}};
    
byte rowPins[NUMROWS] = {9};
byte colPins[NUMCOLS] = {8, 7, 6};

Keypad buttonpad = Keypad(makeKeymap(buttons), rowPins, colPins, NUMROWS, NUMCOLS);
   
byte POT_PIN = A1;

MFRC522 mfrc522(SS_PIN, RST_PIN);   // Create MFRC522 instance.
bool locked = false;
int volume = 0;
unsigned long timePressed = 0;

/* Initialize. */
void setup() {

  Serial.begin(9600); // Initialize serial communications with the PC
  while (!Serial);    // Do nothing if no serial port is opened (added for Arduinos based on ATMEGA32U4)

  SPI.begin();        // Init SPI bus

  mfrc522.PCD_Init(); 
  delay(4); 
  mfrc522.PCD_SetAntennaGain(mfrc522.RxGain_max);
  Serial.println(F("{\"arduino\": true}"));  
  
  // Clear the information stored about locked cards.
  mfrc522.uid.size = 0;
  
  volume = 0;
}


void loop() { 
  // Check potentiometer and buttons
  check_poti();
  check_buttons();
    
  // Wake up all cards present within the sensor/reader range.
  bool cardPresent = PICC_IsAnyCardPresent();
  
  // Reset the loop if no card was locked an no card is present.
  // This saves the select process when no card is found.
  if (! locked && ! cardPresent)
    return;

  // When a card is present (locked) the rest ahead is intensive (constantly checking if still present).
  // Consider including code for checking only at time intervals.

  // Ask for the locked card (if mfrc522uid.size > 0) or for any card if none was locked.
  // (Even if there was some error in the wake up procedure, attempt to contact the locked card.
  // This serves as a double-check to confirm removals.)
  // If a card was locked and now is removed, other cards will not be selected until next loop,
  // after mfrc522uid.size has been set to 0.
  MFRC522::StatusCode result = mfrc522.PICC_Select(&mfrc522.uid,8*mfrc522.uid.size);

  if(!locked && result == MFRC522::STATUS_OK)
  {
    locked=true;
    // Action on card detection.
    print_uid();
  } else if(locked && result != MFRC522::STATUS_OK)
  {
    locked=false;
    mfrc522.uid.size = 0;
    // Action on card removal.
    Serial.println(F("{\"card\": null}"));
  } else if(!locked && result != MFRC522::STATUS_OK)
  {
    // Clear locked card data just in case some data was retrieved in the select procedure
    // but an error prevented locking.
    mfrc522.uid.size = 0;
  }

  mfrc522.PICC_HaltA();     
}

void check_buttons() {
  if (buttonpad.getKeys())
  {
    for (int i = 0; i < LIST_MAX; i++)
    {      
      if (buttonpad.key[i].stateChanged)
      {     
        int button_nr = (int)buttonpad.key[i].kchar;          
        switch (buttonpad.key[i].kstate)
        {        
        case PRESSED: 
          timePressed = millis();           
        case HOLD:  
          if(button_nr != 2){                      
            Serial.print(F("{\"button\": ")); 
            Serial.print(button_nr); 
            Serial.println(F("}"));                                     
          }
          break;
        case RELEASED:    
            unsigned long timeReleased = millis();
            unsigned long buttonDuration = timeReleased - timePressed;                                                 
        case IDLE:
          if(button_nr == 2){ 
            if(buttonDuration > LONGPRESSINTERVAL_MS){
              Serial.print(F("{\"button\": ")); 
              Serial.print(button_nr); 
              Serial.println(F("}"));  
            }   
            else{
              Serial.print(F("{\"button\": ")); 
              Serial.print(3); 
              Serial.println(F("}"));
            }                           
          }                                                                          
          break;
        }
      }
    }
  }
}

void check_poti() {
  int val = analogRead(POT_PIN);
  int vol = (int)((float)val/1024.f*100.f);
  if( abs(vol - volume) > 1){
    volume = vol;
    Serial.print(F("{\"volume\": ")); 
    Serial.print(volume); 
    Serial.println(F("}")); 
  }
}

void print_uid() {
  Serial.print(F("{\"card\": \""));
  dump_byte_array(mfrc522.uid.uidByte, mfrc522.uid.size);
  Serial.println(F("\"}"));
} 

void dump_byte_array(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], HEX);
  }
}

bool PICC_IsAnyCardPresent() {
  byte bufferATQA[2];
  byte bufferSize = sizeof(bufferATQA);
  
  // Reset baud rates
  mfrc522.PCD_WriteRegister(mfrc522.TxModeReg, 0x00);
  mfrc522.PCD_WriteRegister(mfrc522.RxModeReg, 0x00);
  // Reset ModWidthReg
  mfrc522.PCD_WriteRegister(mfrc522.ModWidthReg, 0x26);
  
  MFRC522::StatusCode result = mfrc522.PICC_WakeupA(bufferATQA, &bufferSize);
  return (result == MFRC522::STATUS_OK || result == MFRC522::STATUS_COLLISION);
} // End PICC_IsAnyCardPresent()
