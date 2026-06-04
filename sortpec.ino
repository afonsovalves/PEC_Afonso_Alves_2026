#include "HX711.h"
#include <SoftwareSerial.h>
#include <LobotServoController.h>
const int SCK_PIN = 4;       
const int DOUT1_PIN = 5;   
const int DOUT2_PIN = 6;   
const int DOUT3_PIN = 7;     
const int IMAN_PIN = 9;    
const int RX_PIN = 10;     
const int TX_PIN = 11;       
const unsigned long TEMPO_MEDICAO = 6000; 
const float LIMIAR_PESO = 100.0;  
const int SERVO_MIN = 0;        
const int SERVO_MAX = 1000;
const int TEMPO_MOVIMENTO = 1000;        
float fator_escala_1 = 2010.6; 
float fator_escala_2 = -940.42; 
float fator_escala_3 = -921.14; 
HX711 celula1;
HX711 celula2;
HX711 celula3;
SoftwareSerial servoSerial(RX_PIN, TX_PIN);
LobotServoController controladorServos(servoSerial);
bool cicloConcluido = false;
void setup() {
  Serial.begin(9600);
  servoSerial.begin(9600); 
  Serial.println("--- SISTEMA DE TRIAGEM AUTOMÁTICA ---");
  pinMode(IMAN_PIN, OUTPUT);
  digitalWrite(IMAN_PIN, HIGH); 
  Serial.println("Estado Inicial: Eletroíman LIGADO.");
  celula1.begin(DOUT1_PIN, SCK_PIN);
  celula2.begin(DOUT2_PIN, SCK_PIN);
  celula3.begin(DOUT3_PIN, SCK_PIN); 
  celula1.set_scale(fator_escala_1);
  celula2.set_scale(fator_escala_2);
  celula3.set_scale(fator_escala_3);
  Serial.println("A tarar células com o íman ativo... Não mova o manipulador.");
  celula1.tare();
  celula2.tare();
  celula3.tare();
  Serial.println("Tara concluída. Pronto para operar.");
}
void loop() {
  if (!cicloConcluido) {
    Serial.println("A iniciar o período de medição e estabilização de carga...");
    unsigned long inicioMedicao = millis();
    while (millis() - inicioMedicao < TEMPO_MEDICAO) {
      float c1_temp = celula1.get_units(1);
      float c2_temp = celula2.get_units(1);
      float c3_temp = celula3.get_units(1);
      float peso_total_temp = c1_temp + c2_temp + c3_temp;
      Serial.print("[Tempo Real] C1: ");
      Serial.print(c1_temp, 1);
      Serial.print(" | C2: ");
      Serial.print(c2_temp, 1);
      Serial.print(" | C3: ");
      Serial.print(c3_temp, 1);
      Serial.print(" || TOTAL: ");
      Serial.println(peso_total_temp, 1);
      delay(100); 
    }
    Serial.println("Tempo de estabilização concluído. A efetuar leitura final...");
    float f1 = celula1.get_units(10);
    float f2 = celula2.get_units(10);
    float f3 = celula3.get_units(10);
    float peso_calculado = 1.2*f1+ 1.3*f2 + f3;
    Serial.print("=== Peso total apurado: ");
    Serial.print(peso_calculado);
    Serial.print(" | Limiar definido: ");
    Serial.print(LIMIAR_PESO);
    Serial.println(" ===");
    if (peso_calculado < LIMIAR_PESO) {
      Serial.println("Resultado: ABAIXO DO LIMIAR. A executar Rotina 1...");
      controladorServos.moveServo(1, SERVO_MIN, TEMPO_MOVIMENTO);
      controladorServos.moveServo(2, SERVO_MIN, TEMPO_MOVIMENTO);
      controladorServos.moveServo(3, SERVO_MAX, TEMPO_MOVIMENTO);
      controladorServos.moveServo(1, 500, TEMPO_MOVIMENTO);
      controladorServos.moveServo(2, 500, TEMPO_MOVIMENTO);
      controladorServos.moveServo(3, 500, TEMPO_MOVIMENTO);
      delay(TEMPO_MOVIMENTO + 200); 
      digitalWrite(IMAN_PIN, LOW);
      Serial.println("Eletroíman DESLIGADO. Objeto libertado na Zona 1.");
    } else {
      Serial.println("Resultado: ACIMA DO LIMIAR. A executar Rotina 2...");
      controladorServos.moveServo(1, SERVO_MAX, TEMPO_MOVIMENTO);
      controladorServos.moveServo(2, SERVO_MIN, TEMPO_MOVIMENTO);
      controladorServos.moveServo(3, SERVO_MAX, TEMPO_MOVIMENTO);
      controladorServos.moveServo(1, 500, TEMPO_MOVIMENTO);
      controladorServos.moveServo(2, 500, TEMPO_MOVIMENTO);
      controladorServos.moveServo(3, 500, TEMPO_MOVIMENTO);
      delay(TEMPO_MOVIMENTO + 200);
      digitalWrite(IMAN_PIN, LOW);
      Serial.println("Eletroíman DESLIGADO. Objeto libertado na Zona 2.");
    }
    cicloConcluido = true;
    Serial.println("Ciclo terminado. Reinicie o Arduino para nova triagem.");
  }
}