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

byte buttons[NUMROWS][NUMCOLS] = {
    {0, 1, 2}};
    
byte rowPins[NUMROWS] = {9};
byte colPins[NUMCOLS] = {8, 7, 6};

Keypad buttonpad = Keypad(makeKeymap(buttons), rowPins, colPins, NUMROWS, NUMCOLS);
   
byte POT_PIN = A1;

MFRC522 mfrc522(SS_PIN, RST_PIN);   // Create MFRC522 instance.
bool card_present = false;
int volume = 0;

/* Initialize. */
void setup() {

  Serial.begin(9600); // Initialize serial communications with the PC
  while (!Serial);    // Do nothing if no serial port is opened (added for Arduinos based on ATMEGA32U4)

  SPI.begin();        // Init SPI bus

  mfrc522.PCD_Init();  
  mfrc522.PCD_SetAntennaGain(mfrc522.RxGain_max);
  Serial.println(F("{\"arduino\": true}"));  
  card_present = false;
  volume = 0;
}

/**
 * Main loop.
 */
void loop() {    
  // Look for new cards

  //if(mfrc522.PICC_ReadCardSerial()){
  //  Serial.println("can read card");
  //}
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    if (!card_present) {
      // Show some details of the PICC (that is: the tag/card)
      print_uid();
      mfrc522.PICC_HaltA();
      mfrc522.PCD_StopCrypto1();
    }
    card_present = true;
  }
  else {
    byte atqa_answer[2];
    byte atqa_size = 2;
    mfrc522.PICC_WakeupA(atqa_answer, &atqa_size);
    if (!mfrc522.PICC_ReadCardSerial()) {
      if (card_present) {
        card_present = false;
        Serial.println(F("{\"card\": null}"));
      }      
    }
    else {      
      if( !card_present){
        card_present = true;
        print_uid();
      }
      mfrc522.PICC_HaltA();
      mfrc522.PCD_StopCrypto1();
    }
  }

  int val = analogRead(POT_PIN);
  int vol = (int)((float)val/1024.f*100.f);
  if( vol != volume){
    volume = vol;
    Serial.print(F("{\"volume\": ")); 
    Serial.print(volume); 
    Serial.println(F("}")); 
  }
    
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
        case HOLD:                        
          Serial.print(F("{\"button\": ")); 
          Serial.print(button_nr); 
          Serial.println(F("}"));                                     
          break;
        case RELEASED:                                             
        case IDLE:                                                                                   
          break;
        }
      }
    }
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
