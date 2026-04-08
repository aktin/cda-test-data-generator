<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="aktin_raw">
        <ClinicalDocument xmlns="urn:hl7-org:v3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                          xmlns:sdtc="urn:hl7-org:sdtc" xsi:schemaLocation="urn:hl7-org:v3 ../schemas/CDA.xsd">
            <!--
            CDA Header
            -->
            <!-- Realmcode (fix) -->
            <realmCode code="DE"/>
            <!-- Type Id (fix) -->
            <typeId root="2.16.840.1.113883.1.3" extension="POCD_HD000040"/>
            <!-- Template Id (fix) -->
            <templateId root="1.2.276.0.76.10.1019"/>
            <!-- Identifikation des Dokuments -->
            <id root="1.2.276.0.76.4.17.9814184919" extension="14025fda-3f25-4c64-8883-4f7e6cabc0b6">
                <xsl:attribute name="extension">
                    <xsl:value-of select="document_id"/>
                </xsl:attribute>
            </id>
            <!-- Fixer Dokumententype-Code -->
            <code code="68552-9" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
                  displayName="Emergency medicine Emergency department Admission evaluation note"/>
            <!-- Datum und Zeit der Erstellung -->
            <effectiveTime>
                <xsl:attribute name="value">
                    <xsl:value-of select="date_creation"/>
                </xsl:attribute>
            </effectiveTime>
            <!-- Vertraulichkeitsstufe -->
            <confidentialityCode code="N" codeSystem="2.16.840.1.113883.5.25"/>
            <!-- Sprache und Länderkennung -->
            <languageCode code="de-DE"/>
            <!-- Set-ID und Versionsnummer des Dokuments -->
            <setId root="1.2.276.0.76.4.17.9814184919">
                <xsl:attribute name="extension">
                    <xsl:value-of select="version_id"/>
                </xsl:attribute>
            </setId>
            <versionNumber value="1"/>
            <!-- Patient -->
            <recordTarget typeCode="RCT" contextControlCode="OP">
                <patientRole classCode="PAT">
                    <!-- Identifikation -->
                    <id root="1.2.276.0.76.4.8">
                        <xsl:attribute name="extension">
                            <xsl:value-of select="patient_id"/>
                        </xsl:attribute>
                    </id>
                    <!-- Adresse -->
                    <addr>
                        <streetAddressLine>
                            <xsl:value-of select="street_address_line"/>
                        </streetAddressLine>
                        <xsl:if test="patient_additional_locator != ''">
                            <additionalLocator><xsl:value-of select="patient_additional_locator"/></additionalLocator>
                        </xsl:if>
                        <xsl:if test="patient_direction != ''">
                            <direction><xsl:value-of select="patient_direction"/></direction>
                        </xsl:if>
                        <postalCode>
                            <xsl:value-of select="postal_code"/>
                        </postalCode>
                        <city>
                            <xsl:value-of select="city"/>
                        </city>
                        <xsl:if test="patient_state != ''">
                            <state><xsl:value-of select="patient_state"/></state>
                        </xsl:if>
                    </addr>
                    <!-- Kontakt -->
                    <xsl:if test="patient_phone != ''">
                        <telecom use="HP"><xsl:attribute name="value"><xsl:text>tel:</xsl:text><xsl:value-of select="patient_phone"/></xsl:attribute></telecom>
                    </xsl:if>
                    <xsl:if test="patient_mobile != ''">
                        <telecom use="MC"><xsl:attribute name="value"><xsl:text>tel:</xsl:text><xsl:value-of select="patient_mobile"/></xsl:attribute></telecom>
                    </xsl:if>
                    <xsl:if test="patient_email != ''">
                        <telecom use="HP"><xsl:attribute name="value"><xsl:text>mailto:</xsl:text><xsl:value-of select="patient_email"/></xsl:attribute></telecom>
                    </xsl:if>
                    <patient classCode="PSN" determinerCode="INSTANCE">
                        <!-- Name -->
                        <name>
                            <given>
                                <xsl:value-of select="patient_first_name"/>
                            </given>
                            <family>
                                <xsl:value-of select="patient_last_name"/>
                            </family>
                        </name>
                        <!-- Geschlecht -->
                        <administrativeGenderCode code="M" codeSystem="2.16.840.1.113883.5.1">
                            <xsl:attribute name="code">
                                <xsl:value-of select="gender"/>
                            </xsl:attribute>
                        </administrativeGenderCode>
                        <!-- Geburtsdatum -->
                        <birthTime>
                            <xsl:attribute name="value">
                                <xsl:value-of select="birth_date_ts"/>
                            </xsl:attribute>
                        </birthTime>
                    </patient>
                </patientRole>
            </recordTarget>
            <!-- Author -->
            <author typeCode="AUT" contextControlCode="OP">
                <time>
                    <xsl:attribute name="value">
                        <xsl:value-of select="author_ts"/>
                    </xsl:attribute>
                </time>
                <assignedAuthor classCode="ASSIGNED">
                    <id root="1.2.276.0.76.3.2.123456789">
                        <xsl:if test="author_id != ''">
                            <xsl:attribute name="extension"><xsl:value-of select="author_id"/></xsl:attribute>
                        </xsl:if>
                    </id>
                    <assignedPerson classCode="PSN" determinerCode="INSTANCE">
                        <name>
                            <prefix>
                                <xsl:value-of select="author_prefix"/>
                            </prefix>
                            <given>
                                <xsl:value-of select="author_first_name"/>
                            </given>
                            <family>
                                <xsl:value-of select="author_last_name"/>
                            </family>
                        </name>
                    </assignedPerson>

                    <representedOrganization classCode="ORG" determinerCode="INSTANCE">
                        <id root="1.2.276.0.76.4.17">
                            <xsl:attribute name="extension">
                                <xsl:value-of select="organization_id"/>
                            </xsl:attribute>
                        </id>
                        <name>
                            <xsl:value-of select="organization_name"/>
                        </name>
                        <xsl:if test="organization_street != '' or organization_city != '' or organization_postal_code != ''">
                            <addr>
                                <xsl:if test="organization_street != ''">
                                    <streetAddressLine><xsl:value-of select="organization_street"/></streetAddressLine>
                                </xsl:if>
                                <xsl:if test="organization_additional_locator != ''">
                                    <additionalLocator><xsl:value-of select="organization_additional_locator"/></additionalLocator>
                                </xsl:if>
                                <xsl:if test="organization_postal_code != ''">
                                    <postalCode><xsl:value-of select="organization_postal_code"/></postalCode>
                                </xsl:if>
                                <xsl:if test="organization_city != ''">
                                    <city><xsl:value-of select="organization_city"/></city>
                                </xsl:if>
                                <xsl:if test="organization_state != ''">
                                    <state><xsl:value-of select="organization_state"/></state>
                                </xsl:if>
                            </addr>
                        </xsl:if>
                        <!-- Note: telecom is not permitted in representedOrganization per AKTIN CDA schema -->
                    </representedOrganization>
                </assignedAuthor>
            </author>
            <!-- Zweiter Autor (optional) -->
            <xsl:if test="author_2_first_name != '' or author_2_last_name != ''">
                <author typeCode="AUT" contextControlCode="OP">
                    <time>
                        <xsl:attribute name="value">
                            <xsl:value-of select="author_2_ts"/>
                        </xsl:attribute>
                    </time>
                    <assignedAuthor classCode="ASSIGNED">
                        <id root="1.2.276.0.76.3.2.123456789">
                            <xsl:if test="author_2_id != ''">
                                <xsl:attribute name="extension"><xsl:value-of select="author_2_id"/></xsl:attribute>
                            </xsl:if>
                        </id>
                        <assignedPerson classCode="PSN" determinerCode="INSTANCE">
                            <name>
                                <xsl:if test="author_2_prefix != ''">
                                    <prefix><xsl:value-of select="author_2_prefix"/></prefix>
                                </xsl:if>
                                <given><xsl:value-of select="author_2_first_name"/></given>
                                <family><xsl:value-of select="author_2_last_name"/></family>
                            </name>
                        </assignedPerson>
                        <representedOrganization classCode="ORG" determinerCode="INSTANCE">
                            <id root="1.2.276.0.76.4.17">
                                <xsl:attribute name="extension">
                                    <xsl:value-of select="organization_id"/>
                                </xsl:attribute>
                            </id>
                            <name>
                                <xsl:value-of select="organization_name"/>
                            </name>
                        </representedOrganization>
                    </assignedAuthor>
                </author>
            </xsl:if>
            <!-- Verwaltungsorganisation des Dokuments -->
            <custodian>
                <assignedCustodian>
                    <representedCustodianOrganization>
                        <id root="1.2.276.0.76.4.17">
                            <xsl:attribute name="extension">
                                <xsl:value-of select="organization_id"/>
                            </xsl:attribute>
                        </id>
                        <name>
                            <xsl:value-of select="organization_name"/>
                        </name>
                        <xsl:if test="organization_street != '' or organization_city != '' or organization_postal_code != ''">
                            <addr>
                                <xsl:if test="organization_street != ''">
                                    <streetAddressLine><xsl:value-of select="organization_street"/></streetAddressLine>
                                </xsl:if>
                                <xsl:if test="organization_additional_locator != ''">
                                    <additionalLocator><xsl:value-of select="organization_additional_locator"/></additionalLocator>
                                </xsl:if>
                                <xsl:if test="organization_postal_code != ''">
                                    <postalCode><xsl:value-of select="organization_postal_code"/></postalCode>
                                </xsl:if>
                                <xsl:if test="organization_city != ''">
                                    <city><xsl:value-of select="organization_city"/></city>
                                </xsl:if>
                                <xsl:if test="organization_state != ''">
                                    <state><xsl:value-of select="organization_state"/></state>
                                </xsl:if>
                            </addr>
                        </xsl:if>
                        <!-- Note: telecom is not permitted in representedOrganization per AKTIN CDA schema -->
                    </representedCustodianOrganization>
                </assignedCustodian>
            </custodian>
            <!-- Kostenträger/Versicherung -->


            <participant typeCode="HLD">
                <templateId root="1.2.276.0.76.10.2022"/>
                <time>
                    <!-- Quartalsende: CSV versicherungs_quartalsende (YYYYMMDD); fallback to fixed value -->
                    <high>
                        <xsl:attribute name="value">
                            <xsl:choose>
                                <xsl:when test="insurance_quarter_end != ''"><xsl:value-of select="insurance_quarter_end"/></xsl:when>
                                <xsl:otherwise>20231231</xsl:otherwise>
                            </xsl:choose>
                        </xsl:attribute>
                    </high>
                </time>
                <associatedEntity classCode="POLHOLD">
                    <!-- eGK Nummer: root must not coexist with nullFlavor (dtr1-2-II) -->
                    <id>
                        <xsl:choose>
                            <xsl:when test="insurance_egk = ''">
                                <xsl:attribute name="nullFlavor"><xsl:text>UNK</xsl:text></xsl:attribute>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:attribute name="root">1.2.276.0.76.4.8</xsl:attribute>
                                <xsl:attribute name="extension">
                                    <xsl:value-of select="insurance_egk"/>
                                </xsl:attribute>
                            </xsl:otherwise>
                        </xsl:choose>
                    </id>
                    <!-- Versicherungsnummer (omitted when empty) -->
                    <xsl:if test="insurance_number != ''">
                        <id root="1.2.276.0.76.3.1.131.1.4.3.9999.9999.999955">
                            <xsl:attribute name="extension"><xsl:value-of select="insurance_number"/></xsl:attribute>
                        </id>
                    </xsl:if>
                    <code code="SELF" codeSystem="2.16.840.1.113883.5.111" displayName="self">
                        <xsl:attribute name="code">
                            <xsl:value-of select="insurance_case"/>
                        </xsl:attribute>
                    </code>
                    <xsl:if test="insurance_case = 'FAMDEP'">
                        <associatedPerson>
                            <name>
                                <given>
                                    <xsl:value-of select="_associated_person_first_name"/>
                                </given>
                                <family>
                                    <xsl:value-of select="_associated_person_last_name"/>
                                </family>
                            </name>
                        </associatedPerson>
                    </xsl:if>
                    <scopingOrganization>
                        <!-- IK-NR (omitted when empty — extension cannot be empty per XSD 'st') -->
                        <xsl:if test="string(insurance_iknr) != ''">
                            <id root="1.2.276.0.76.4.5">
                                <xsl:attribute name="extension">
                                    <xsl:value-of select="insurance_iknr"/>
                                </xsl:attribute>
                            </id>
                        </xsl:if>
                        <!-- VK-NR (omitted when empty) -->
                        <xsl:if test="insurance_vk != ''">
                            <id root="1.2.276.0.76.4.7">
                                <xsl:attribute name="extension"><xsl:value-of select="insurance_vk"/></xsl:attribute>
                            </id>
                        </xsl:if>
                        <name>
                            <xsl:value-of select="insurance_txt"/>
                        </name>
                    </scopingOrganization>
                </associatedEntity>
            </participant>

            <!-- Aufnahme -->
            <documentationOf typeCode="DOC">
                <serviceEvent classCode="ACT" moodCode="EVN">
                    <!-- Behandlung -->
                    <effectiveTime>
                        <!-- Start der Behandlung (Datum und Zeit), Therapiebeginn, Zeitangabe genau bis auf die Minute -->
                        <low>
                            <xsl:attribute name="value">
                                <xsl:value-of select="therapy_start_ts"/>
                            </xsl:attribute>
                        </low>
                        <!-- Therapieende (therapieende_zeitpunkt); falls back to discharge_ts if empty -->
                        <high>
                            <xsl:attribute name="value">
                                <xsl:choose>
                                    <xsl:when test="therapy_end_ts != ''"><xsl:value-of select="therapy_end_ts"/></xsl:when>
                                    <xsl:otherwise><xsl:value-of select="discharge_ts"/></xsl:otherwise>
                                </xsl:choose>
                            </xsl:attribute>
                        </high>
                    </effectiveTime>
                    <performer typeCode="PRF">
                        <!-- Erster Arzt, Arztkontakt Beginn und Ende -->
                        <time>
                            <!-- Begin des Arztkontaktes -->
                            <low>
                                <xsl:attribute name="value">
                                    <xsl:value-of select="doctor_contact_ts"/>
                                </xsl:attribute>
                            </low>
                            <!-- Ende des Arztkontaktes -->
                            <high>
                                <xsl:attribute name="value">
                                    <xsl:value-of select="end_doctor_contact_ts"/>
                                </xsl:attribute>
                            </high>
                        </time>
                        <assignedEntity classCode="ASSIGNED">
                            <!-- AKTIN schematron (CDADocumentationOf) requires nullFlavor="NA" here;
                                 behandler_id is mapped in field dict but not emitted in CDA -->
                            <id nullFlavor="NA"/>
                        </assignedEntity>
                    </performer>
                </serviceEvent>
            </documentationOf>
            <!-- Patientenkontakt -->
            <componentOf>
                <encompassingEncounter classCode="ENC" moodCode="EVN">
                    <!-- Encounter-ID (Patientenkontakt in der Notaufnahme) -->
                    <id root="1.2.276.0.76.3.87686">
                        <xsl:attribute name="extension">
                            <xsl:value-of select="admission_id"/>
                        </xsl:attribute>
                    </id>
                    <!-- Krankenhausinternes Fallkennzeichen (optional) -->
                    <xsl:if test="string(case_number) != ''">
                        <id>
                            <xsl:attribute name="root">
                                <xsl:value-of select="case_number_oid"/>
                            </xsl:attribute>
                            <xsl:attribute name="extension">
                                <xsl:value-of select="case_number"/>
                            </xsl:attribute>
                        </id>
                    </xsl:if>
                    <effectiveTime>
                        <!-- Start Patientenkontakt -->
                        <low>
                            <xsl:attribute name="value">
                                <xsl:value-of select="admission_ts"/>
                            </xsl:attribute>
                        </low>
                        <!-- Ende Patientenkontakt = Zeitpunkt der Verlegung/Entlassung -->
                        <high>
                            <xsl:attribute name="value">
                                <xsl:value-of select="discharge_ts"/>
                            </xsl:attribute>
                        </high>
                    </effectiveTime>
                    <!-- Entlassung ODER Verlegung — niemals beides (Schematron-Regel) -->
                    <xsl:if test="verlegung_type = '' or verlegung_type = 'OTH'">
                        <dischargeDispositionCode>
                            <xsl:choose>
                                <xsl:when test="discharge = ''">
                                    <xsl:attribute name="nullFlavor">
                                        <xsl:text>OTH</xsl:text>
                                    </xsl:attribute>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:attribute name="code">
                                        <xsl:value-of select="discharge"/>
                                    </xsl:attribute>
                                    <xsl:attribute name="codeSystem">
                                        <xsl:text>1.2.276.0.76.3.1.195.5.56</xsl:text>
                                    </xsl:attribute>
                                </xsl:otherwise>
                            </xsl:choose>
                        </dischargeDispositionCode>
                    </xsl:if>
                </encompassingEncounter>
            </componentOf>

            <!--
                CDA Body
            -->
            <component>
                <structuredBody>
                    <component typeCode="COMP" contextConductionInd="true">
                        <!-- Transportmittel -->
                        <section classCode="DOCSECT">
                            <templateId root="1.2.276.0.76.10.3045"/>
                            <code code="11459-5" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
                                  displayName="Transport mode"/>
                            <title>Transportmittel</title>
                            <text>&#160;</text>
                            <entry typeCode="COMP">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4037"/>
                                    <code code="11459-5" codeSystem="2.16.840.1.113883.6.1"
                                          displayName="Transport method"/>
                                    <statusCode code="completed"/>
                                    <!-- Optional: Ankunftszeit -->
                                    <effectiveTime>
                                        <high>
                                            <xsl:attribute name="value">
                                                <xsl:value-of select="admission_ts"/>
                                            </xsl:attribute>
                                        </high>
                                    </effectiveTime>
                                    <value xsi:type="CV">
                                        <xsl:choose>
                                            <xsl:when test="transport_method = 'NA' or transport_method = 'OTH'">
                                                <xsl:attribute name="nullFlavor">
                                                    <xsl:value-of select="transport_method"/>
                                                </xsl:attribute>
                                            </xsl:when>
                                            <xsl:when test="transport_method = ''">
                                                <xsl:attribute name="nullFlavor">
                                                    <xsl:text>UNK</xsl:text>
                                                </xsl:attribute>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:attribute name="codeSystem">
                                                    <xsl:text>1.2.276.0.76.3.1.195.5.41</xsl:text>
                                                </xsl:attribute>
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="transport_method"/>
                                                </xsl:attribute>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </value>
                                </observation>
                            </entry>
                        </section>
                    </component>

                    <!-- Zuweisung -->
                    <component typeCode="COMP" contextConductionInd="true">
                        <section classCode="DOCSECT">
                            <templateId root="1.2.276.0.76.10.3046"/>
                            <code code="11293-8" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
                                  displayName="Type of Referral source"/>
                            <title>Zuweisung</title>
                            <text>KV-Notdienst</text>
                            <entry typeCode="COMP">
                                <act classCode="PCPR" moodCode="RQO">
                                    <templateId root="1.2.276.0.76.10.4038"/>
                                    <code code="11293-8" codeSystem="2.16.840.1.113883.6.1" displayName="Zuweisung"/>
                                    <participant typeCode="AUT">
                                        <participantRole classCode="AGNT">
                                            <xsl:choose>
                                                <xsl:when test="referral = 'OTH' or referral = ''">
                                                    <code nullFlavor="OTH"/>
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <code codeSystem="1.2.276.0.76.5.440">
                                                        <xsl:attribute name="code">
                                                            <xsl:value-of select="referral"/>
                                                        </xsl:attribute>
                                                    </code>
                                                </xsl:otherwise>
                                            </xsl:choose>
                                        </participantRole>
                                    </participant>
                                </act>
                            </entry>
                        </section>
                    </component>

                    <component typeCode="COMP" contextConductionInd="true">
                        <!-- Notfallanamnese -->
                        <section classCode="DOCSECT">
                            <templateId root="1.2.276.0.76.10.3053"/>
                            <code code="10164-2" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
                                  displayName="History of present illness"/>
                            <title>Notfallanamnese</title>
                            <text>
                                <xsl:choose>
                                    <xsl:when test="emergency_medical_history = ''">
                                        <xsl:text>&#160;</xsl:text>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:value-of select="emergency_medical_history"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </text>
                        </section>
                    </component>

                    <component typeCode="COMP" contextConductionInd="true">
                        <!-- Beschwerden bei Vorstellung -->
                        <section classCode="DOCSECT">
                            <templateId root="1.2.276.0.76.10.3048"/>
                            <code code="46239-0" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
                                  displayName="Chief complaint+Reason for visit"/>
                            <title>Beschwerden bei Vorstellung</title>
                            <text>
                                <content ID="compl-1">
                                    <xsl:value-of select="complaint_list"/>
                                </content>
                            </text>
                            <entry typeCode="COMP">
                                <act classCode="ACT" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4039"/>
                                    <id root="1.2.276.0.76.4.17.9814184919">
                                        <xsl:attribute name="extension">
                                            <xsl:value-of select="concat(document_id, '-compl-act')"/>
                                        </xsl:attribute>
                                    </id>
                                    <code code="CONC" codeSystem="2.16.840.1.113883.5.6" displayName="Concern"/>
                                    <statusCode code="active"/>
                                    <effectiveTime>
                                        <low>
                                            <xsl:choose>
                                                <xsl:when test="complaint_start = ''">
                                                    <xsl:attribute name="nullFlavor">
                                                        <xsl:text>UNK</xsl:text>
                                                    </xsl:attribute>
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <xsl:attribute name="value">
                                                        <xsl:value-of select="complaint_start"/>
                                                    </xsl:attribute>
                                                </xsl:otherwise>
                                            </xsl:choose>
                                        </low>
                                    </effectiveTime>
                                    <entryRelationship typeCode="SUBJ">
                                        <observation classCode="OBS" moodCode="EVN">
                                            <templateId root="1.2.276.0.76.10.4040"/>
                                            <id root="1.2.276.0.76.4.17.9814184919">
                                                <xsl:attribute name="extension">
                                                    <xsl:value-of select="concat(document_id, '-compl-obs')"/>
                                                </xsl:attribute>
                                            </id>
                                            <code code="75322-8" codeSystem="2.16.840.1.113883.6.1"
                                                  displayName="Complaint"/>
                                            <text>
                                                <reference value="#compl-1"/>
                                            </text>
                                            <statusCode code="completed"/>
                                            <effectiveTime>
                                                <width>
                                                    <xsl:choose>
                                                        <xsl:when test="symptom_duration = ''">
                                                            <xsl:attribute name="nullFlavor">
                                                                <xsl:text>UNK</xsl:text>
                                                            </xsl:attribute>
                                                        </xsl:when>
                                                        <xsl:otherwise>
                                                            <xsl:attribute name="value">
                                                                <xsl:value-of select="symptom_duration"/>
                                                            </xsl:attribute>
                                                            <xsl:attribute name="unit">
                                                                <xsl:text>h</xsl:text>
                                                            </xsl:attribute>
                                                        </xsl:otherwise>
                                                    </xsl:choose>
                                                </width>
                                            </effectiveTime>
                                            <value xsi:type="CE">
                                                <xsl:choose>
                                                    <xsl:when test="cedis = ''">
                                                        <xsl:attribute name="nullFlavor">
                                                            <xsl:text>UNK</xsl:text>
                                                        </xsl:attribute>
                                                    </xsl:when>
                                                    <xsl:when test="cedis = 'OTH'">
                                                        <xsl:attribute name="nullFlavor">
                                                            <xsl:text>OTH</xsl:text>
                                                        </xsl:attribute>
                                                        <originalText>
                                                            <xsl:choose>
                                                                <xsl:when test="string(complaints_txt) = ''">
                                                                    <xsl:text>&#160;</xsl:text>
                                                                </xsl:when>
                                                                <xsl:otherwise>
                                                                    <xsl:value-of select="complaints_txt"/>
                                                                </xsl:otherwise>
                                                            </xsl:choose>
                                                        </originalText>
                                                    </xsl:when>
                                                    <xsl:otherwise>
                                                        <xsl:attribute name="code">
                                                            <xsl:value-of select="cedis"/>
                                                        </xsl:attribute>
                                                        <xsl:attribute name="codeSystem">
                                                            <xsl:text>1.2.276.0.76.5.439</xsl:text>
                                                        </xsl:attribute>
                                                        <originalText>
                                                            <xsl:choose>
                                                                <xsl:when test="string(complaints_txt) = ''">
                                                                    <xsl:text>&#160;</xsl:text>
                                                                </xsl:when>
                                                                <xsl:otherwise>
                                                                    <xsl:value-of select="complaints_txt"/>
                                                                </xsl:otherwise>
                                                            </xsl:choose>
                                                        </originalText>
                                                    </xsl:otherwise>
                                                </xsl:choose>
                                            </value>
                                        </observation>
                                    </entryRelationship>
                                </act>
                            </entry>
                        </section>
                    </component>

                    <!-- Ersteinschätzung -->
                    <component typeCode="COMP" contextConductionInd="true">
                        <section classCode="DOCSECT">
                            <templateId root="1.2.276.0.76.10.3049"/>
                            <code code="11283-9" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
                                  displayName="Acuity assessment"/>
                            <title>Ersteinschätzung</title>
                            <text>
                                <xsl:choose>
                                    <xsl:when test="initial_assessment_text = ''">
                                        <xsl:text>&#160;</xsl:text>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:value-of select="initial_assessment_text"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </text>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4042"/>
                                    <id root="1.2.276.0.76.4.17.9814184919">
                                        <xsl:attribute name="extension">
                                            <xsl:value-of select="concat(document_id, '-triage')"/>
                                        </xsl:attribute>
                                    </id>
                                    <code code="11283-9" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
                                          displayName="Acuity assessment"/>
                                    <text>
                                        <reference value="#triage"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime>
                                        <xsl:choose>
                                            <xsl:when test="triage_ts_start = ''">
                                                <low nullFlavor="UNK"/>
                                                <high nullFlavor="UNK"/>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <low>
                                                    <xsl:attribute name="value">
                                                        <xsl:value-of select="triage_ts_start"/>
                                                    </xsl:attribute>
                                                </low>
                                                <high>
                                                    <xsl:attribute name="value">
                                                        <xsl:value-of select="triage_ts_end"/>
                                                    </xsl:attribute>
                                                </high>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </effectiveTime>
                                    <value>
                                        <xsl:choose>
                                            <xsl:when test="triage != '' and triage_system != ''">
                                                <xsl:attribute name="xsi:type" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">CE</xsl:attribute>
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="triage"/>
                                                </xsl:attribute>
                                                <xsl:attribute name="codeSystem">
                                                    <xsl:value-of select="triage_system"/>
                                                </xsl:attribute>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:attribute name="xsi:type" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">ST</xsl:attribute>
                                                <xsl:attribute name="nullFlavor">UNK</xsl:attribute>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </value>
                                    <!--<value xsi:type="CE" code="3" codeSystem="1.2.276.0.76.5.438" displayName="Triage"/>-->
                                </observation>
                            </entry>
                        </section>
                    </component>

                    <!-- Klinische Basisinformationen -->
                    <component typeCode="COMP" contextConductionInd="true">
                        <section classCode="DOCSECT">
                            <templateId root="1.2.276.0.76.10.3047"/>
                            <code code="55752-0" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
                                  displayName="Clinical information"/>
                            <title>Klinische Basisinformationen</title>
                            <text>


                                ||Schwanger:|<xsl:value-of select="pregnancy"/>|

                                ||Rankin Skala Score:|<xsl:value-of select="rankin"/>|

                                |Multi|
                                <xsl:value-of select="germs"/>
                                |Multi|
                                |Verdacht|CONF|Verdacht|


                            </text>

                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4043"/>
                                    <id root="1.2.276.0.76.4.17.9814184919">
                                        <xsl:attribute name="extension">
                                            <xsl:value-of select="concat(document_id, '-preg')"/>
                                        </xsl:attribute>
                                    </id>
                                    <code code="11449-6" codeSystem="2.16.840.1.113883.6.1"
                                          displayName="Pregnancy status"/>
                                    <text>
                                        <reference value="#Preg"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime>
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="vital_signs_ts"/>
                                        </xsl:attribute>
                                    </effectiveTime>
                                    <value xsi:type="CV">
                                        <xsl:choose>
                                            <xsl:when test="pregnancy = ''">
                                                <xsl:attribute name="nullFlavor">
                                                    <xsl:text>UNK</xsl:text>
                                                </xsl:attribute>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="pregnancy"/>
                                                </xsl:attribute>
                                                <xsl:attribute name="codeSystem">
                                                    <xsl:text>1.2.276.0.76.3.1.195.5.46</xsl:text>
                                                </xsl:attribute>
                                            </xsl:otherwise>
                                        </xsl:choose>

                                    </value>
                                    <!-- <value xsi:type="CV" code="#Pregnancy#" codeSystem="1.2.276.0.76.3.1.195.5.46" displayName="Patient nicht schwanger"/>-->
                                </observation>
                            </entry>

                            <entry typeCode="COMP" contextConductionInd="true">
                                <substanceAdministration moodCode="EVN" classCode="SBADM">
                                    <xsl:choose>
                                        <xsl:when test="string(tetanus_vaccination) = ''">
                                            <xsl:attribute name="negationInd">
                                                <xsl:text>false</xsl:text>
                                            </xsl:attribute>
                                            <xsl:attribute name="nullFlavor">
                                                <xsl:text>NI</xsl:text>
                                            </xsl:attribute>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <xsl:attribute name="negationInd">
                                                <xsl:value-of select="tetanus_vaccination"/>
                                            </xsl:attribute>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                    <templateId root="1.2.276.0.76.10.4044"/>
                                    <code code="IMMUNIZ" codeSystem="2.16.840.1.113883.5.4"/>
                                    <text>
                                        <reference value="#immun1"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <consumable>
                                        <manufacturedProduct classCode="MANU">
                                            <manufacturedMaterial>
                                                <code code="CTVACC" codeSystem="1.2.276.0.76.3.1.195.5.3"
                                                      displayName="Tetanus vaccine (product)"/>
                                            </manufacturedMaterial>
                                        </manufacturedProduct>
                                    </consumable>
                                </substanceAdministration>
                            </entry>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4045"/>
                                    <id root="1.2.276.0.76.4.17.9814184919">
                                        <xsl:attribute name="extension">
                                            <xsl:value-of select="concat(document_id, '-rankin')"/>
                                        </xsl:attribute>
                                    </id>
                                    <code code="75859-9" codeSystem="2.16.840.1.113883.6.1"
                                          displayName="Modified Rankin scale"/>
                                    <text>
                                        <reference value="#rankin"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime>
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="vital_signs_ts"/>
                                        </xsl:attribute>
                                    </effectiveTime>
                                    <value xsi:type="PQ"
                                           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                                        <xsl:attribute name="value">
                                            <xsl:choose>
                                                <xsl:when test="rankin = ''">0</xsl:when>
                                                <xsl:otherwise><xsl:value-of select="rankin"/></xsl:otherwise>
                                            </xsl:choose>
                                        </xsl:attribute>
                                        <xsl:attribute name="unit">
                                            <xsl:text>{score}</xsl:text>
                                        </xsl:attribute>
                                    </value>
                                </observation>
                            </entry>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <act classCode="ACT" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4072"/>
                                    <id root="1.2.276.0.76.4.17.9814184919">
                                        <xsl:attribute name="extension">
                                            <xsl:value-of select="concat(document_id, '-germs-act')"/>
                                        </xsl:attribute>
                                    </id>
                                    <code code="CONC" codeSystem="2.16.840.1.113883.5.6" displayName="Concern"/>
                                    <statusCode code="completed"/>
                                    <entryRelationship typeCode="SUBJ">
                                        <observation classCode="OBS" moodCode="EVN">
                                            <templateId root="1.2.276.0.76.10.4073"/>
                                            <id root="1.2.276.0.76.4.17.9814184919">
                                                <xsl:attribute name="extension">
                                                    <xsl:value-of select="concat(document_id, '-germs-obs')"/>
                                                </xsl:attribute>
                                            </id>
                                            <code code="COND" codeSystem="2.16.840.1.113883.5.4"
                                                  displayName="Condition"/>
                                            <text>
                                                <reference value="#mdro-1"/>
                                            </text>
                                            <statusCode code="completed"/>
                                            <effectiveTime>
                                                <low value="20150304"/>
                                            </effectiveTime>
                                            <value codeSystem="1.2.276.0.76.5.441" xsi:type="CD">
                                                <xsl:choose>
                                                    <xsl:when test="germs = ''">
                                                        <xsl:attribute name="nullFlavor">
                                                            <xsl:text>OTH</xsl:text>
                                                        </xsl:attribute>
                                                    </xsl:when>
                                                    <xsl:otherwise>
                                                        <xsl:attribute name="code">
                                                            <xsl:value-of select="germs"/>
                                                        </xsl:attribute>
                                                    </xsl:otherwise>
                                                </xsl:choose>
                                            </value>
                                        </observation>
                                    </entryRelationship>
                                </act>
                            </entry>
                        </section>
                    </component>


                    <!-- Diagnostik -->
                    <component typeCode="COMP" contextConductionInd="true">
                        <section classCode="DOCSECT">
                            <templateId root="1.2.276.0.76.10.3050"/>
                            <code code="30954-2" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
                                  displayName="Relevant diagnostic tests &amp;or laboratory data"/>
                            <title>Diagnostik</title>
                            <text>
                                <list>
                                    <item ID="proc-1">
                                        <xsl:value-of select="diagnostics_txt"/>
                                    </item>
                                </list>
                            </text>
                            <xsl:choose>
                                <xsl:when
                                        test="diagnostics_xray_thorax = 'PB' or diagnostics_xray_thorax = 'OPB'">
                                    <entry typeCode="COMP" contextConductionInd="true">
                                        <observation classCode="OBS" moodCode="EVN">
                                            <templateId root="1.2.276.0.76.10.4050"/>
                                            <id root="1.2.276.0.76.4.17.9814184919">
                                                <xsl:attribute name="extension">
                                                    <xsl:value-of select="concat(document_id, '-diag-01')"/>
                                                </xsl:attribute>
                                            </id>
                                            <code code="30745-4" codeSystem="2.16.840.1.113883.6.1"
                                                  displayName="Chest X-ray"/>
                                            <text>
                                                <reference value="#proc-1"/>
                                            </text>
                                            <statusCode code="completed"/>
                                            <effectiveTime value="201501171650">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="diagnostics_ts"/>
                                                </xsl:attribute>
                                            </effectiveTime>
                                            <value xsi:type="CE" codeSystem="1.2.276.0.76.3.1.195.5.51"
                                                   displayName="Chest X-Ray">
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="diagnostics_xray_thorax"/>
                                                </xsl:attribute>
                                            </value>
                                            <participant typeCode="LOC">
                                                <participantRole classCode="SDLOC">
                                                    <code code="ER" codeSystem="2.16.840.1.113883.5.111"
                                                          displayName="Notaufnahme"/>
                                                </participantRole>
                                            </participant>
                                        </observation>
                                    </entry>
                                </xsl:when>
                            </xsl:choose>
                            <xsl:choose>
                                <xsl:when
                                        test="diagnostics_xray_spine = 'PB' or diagnostics_xray_spine = 'OPB'">
                                    <entry typeCode="COMP" contextConductionInd="true">

                                        <observation classCode="OBS" moodCode="EVN">
                                            <templateId root="1.2.276.0.76.10.4051"/>
                                            <id root="1.2.276.0.76.4.17.9814184919">
                                                <xsl:attribute name="extension">
                                                    <xsl:value-of select="concat(document_id, '-diag-02')"/>
                                                </xsl:attribute>
                                            </id>
                                            <code code="38008-9" codeSystem="2.16.840.1.113883.6.1"
                                                  displayName="Spine Cervical and Thoracic and Lumbar X-ray"/>
                                            <text>
                                                <reference value="#proc-2"/>
                                            </text>
                                            <statusCode code="completed"/>
                                            <effectiveTime value="201501171650">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="diagnostics_ts"/>
                                                </xsl:attribute>
                                            </effectiveTime>
                                            <value xsi:type="CE" codeSystem="1.2.276.0.76.3.1.195.5.51">
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="diagnostics_xray_spine"/>
                                                </xsl:attribute>
                                            </value>
                                            <participant typeCode="LOC">
                                                <participantRole classCode="SDLOC">
                                                    <code code="ER" codeSystem="2.16.840.1.113883.5.111"
                                                          displayName="Notaufnahme"/>
                                                </participantRole>
                                            </participant>
                                        </observation>
                                    </entry>
                                </xsl:when>
                            </xsl:choose>
                            <xsl:choose>
                                <xsl:when
                                        test="diagnostics_xray_pelvis = 'PB' or diagnostics_xray_pelvis = 'OPB'">
                                    <entry typeCode="COMP" contextConductionInd="true">

                                        <observation classCode="OBS" moodCode="EVN">
                                            <templateId root="1.2.276.0.76.10.4052"/>
                                            <id root="1.2.276.0.76.4.17.9814184919">
                                                <xsl:attribute name="extension">
                                                    <xsl:value-of select="concat(document_id, '-diag-03')"/>
                                                </xsl:attribute>
                                            </id>
                                            <code code="28561-9" codeSystem="2.16.840.1.113883.6.1"
                                                  displayName="Pelvis X-Ray"/>
                                            <text>
                                                <reference value="#proc-2"/>
                                            </text>
                                            <statusCode code="completed"/>
                                            <effectiveTime value="201501171650">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="diagnostics_ts"/>
                                                </xsl:attribute>
                                            </effectiveTime>
                                            <value xsi:type="CE" codeSystem="1.2.276.0.76.3.1.195.5.51">
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="diagnostics_xray_pelvis"/>
                                                </xsl:attribute>
                                            </value>
                                            <participant typeCode="LOC">
                                                <participantRole classCode="SDLOC">
                                                    <code code="ER" codeSystem="2.16.840.1.113883.5.111"
                                                          displayName="Notaufnahme"/>
                                                </participantRole>
                                            </participant>
                                        </observation>
                                    </entry>
                                </xsl:when>
                            </xsl:choose>
                            <xsl:choose>
                                <xsl:when
                                        test="diagnostics_xray_extremities = 'PB' or diagnostics_xray_extremities = 'OPB'">
                                    <entry typeCode="COMP" contextConductionInd="true">

                                        <observation classCode="OBS" moodCode="EVN">
                                            <templateId root="1.2.276.0.76.10.4053"/>
                                            <id root="1.2.276.0.76.4.17.9814184919">
                                                <xsl:attribute name="extension">
                                                    <xsl:value-of select="concat(document_id, '-diag-04')"/>
                                                </xsl:attribute>
                                            </id>
                                            <code code="37637-6" codeSystem="2.16.840.1.113883.6.1"
                                                  displayName="Extremity X-Ray"/>
                                            <text>
                                                <reference value="#proc-4"/>
                                            </text>
                                            <statusCode code="completed"/>
                                            <effectiveTime value="201501171650">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="diagnostics_ts"/>
                                                </xsl:attribute>
                                            </effectiveTime>
                                            <value xsi:type="CE" codeSystem="1.2.276.0.76.3.1.195.5.51">
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="diagnostics_xray_extremities"/>
                                                </xsl:attribute>
                                            </value>
                                            <participant typeCode="LOC">
                                                <participantRole classCode="SDLOC">
                                                    <code code="ER" codeSystem="2.16.840.1.113883.5.111"
                                                          displayName="Notaufnahme"/>
                                                </participantRole>
                                            </participant>
                                        </observation>
                                    </entry>
                                </xsl:when>
                            </xsl:choose>
                            <xsl:choose>
                                <xsl:when
                                        test="diagnostics_xray_others = 'PB' or diagnostics_xray_others = 'OPB'">
                                    <entry typeCode="COMP" contextConductionInd="true">

                                        <observation classCode="OBS" moodCode="EVN">
                                            <templateId root="1.2.276.0.76.10.4054"/>
                                            <id root="1.2.276.0.76.4.17.9814184919">
                                                <xsl:attribute name="extension">
                                                    <xsl:value-of select="concat(document_id, '-diag-05')"/>
                                                </xsl:attribute>
                                            </id>
                                            <code code="43468-8" codeSystem="2.16.840.1.113883.6.1"
                                                  displayName="Unspecified body region X-Ray"/>
                                            <text>
                                                <reference value="#proc-5"/>
                                            </text>
                                            <statusCode code="completed"/>
                                            <effectiveTime value="201501171650">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="diagnostics_ts"/>
                                                </xsl:attribute>
                                            </effectiveTime>
                                            <value xsi:type="CE" codeSystem="1.2.276.0.76.3.1.195.5.51">
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="diagnostics_xray_others"/>
                                                </xsl:attribute>
                                            </value>
                                            <participant typeCode="LOC">
                                                <participantRole classCode="SDLOC">
                                                    <code code="ER" codeSystem="2.16.840.1.113883.5.111"
                                                          displayName="Notaufnahme"/>
                                                </participantRole>
                                            </participant>
                                        </observation>
                                    </entry>
                                </xsl:when>
                            </xsl:choose>
                            <xsl:choose>
                                <xsl:when
                                        test="diagnostics_ct_head = 'PB' or diagnostics_ct_head = 'OPB'">
                                    <entry typeCode="COMP" contextConductionInd="true">

                                        <observation classCode="OBS" moodCode="EVN">
                                            <templateId root="1.2.276.0.76.10.4055"/>
                                            <id root="1.2.276.0.76.4.17.9814184919">
                                                <xsl:attribute name="extension">
                                                    <xsl:value-of select="concat(document_id, '-diag-06')"/>
                                                </xsl:attribute>
                                            </id>
                                            <code code="24725-4" codeSystem="2.16.840.1.113883.6.1"
                                                  displayName="Head CT"/>
                                            <text>
                                                <reference value="#proc-6"/>
                                            </text>
                                            <statusCode code="completed"/>
                                            <effectiveTime value="201501171650">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="diagnostics_ts"/>
                                                </xsl:attribute>
                                            </effectiveTime>
                                            <value xsi:type="CE" codeSystem="1.2.276.0.76.3.1.195.5.51">
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="diagnostics_ct_head"/>
                                                </xsl:attribute>
                                            </value>
                                            <participant typeCode="LOC">
                                                <participantRole classCode="SDLOC">
                                                    <code code="ER" codeSystem="2.16.840.1.113883.5.111"
                                                          displayName="Notaufnahme"/>
                                                </participantRole>
                                            </participant>
                                        </observation>
                                    </entry>
                                </xsl:when>
                            </xsl:choose>
                            <xsl:choose>
                                <xsl:when
                                        test="diagnostics_ct = 'PB' or diagnostics_ct = 'OPB'">
                                    <entry typeCode="COMP" contextConductionInd="true">

                                        <observation classCode="OBS" moodCode="EVN">
                                            <templateId root="1.2.276.0.76.10.4056"/>
                                            <id root="1.2.276.0.76.4.17.9814184919">
                                                <xsl:attribute name="extension">
                                                    <xsl:value-of select="concat(document_id, '-diag-07')"/>
                                                </xsl:attribute>
                                            </id>
                                            <code code="46305-9" codeSystem="2.16.840.1.113883.6.1"
                                                  displayName="CT whole body"/>
                                            <text>
                                                <reference value="#proc-7"/>
                                            </text>
                                            <statusCode code="completed"/>
                                            <effectiveTime value="201501171650">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="diagnostics_ts"/>
                                                </xsl:attribute>
                                            </effectiveTime>
                                            <value xsi:type="CE" codeSystem="1.2.276.0.76.3.1.195.5.51">
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="diagnostics_ct"/>
                                                </xsl:attribute>
                                            </value>
                                            <participant typeCode="LOC">
                                                <participantRole classCode="SDLOC">
                                                    <code code="ER" codeSystem="2.16.840.1.113883.5.111"
                                                          displayName="Notaufnahme"/>
                                                </participantRole>
                                            </participant>
                                        </observation>
                                    </entry>
                                </xsl:when>
                            </xsl:choose>

                            <xsl:choose>
                                <xsl:when
                                        test="diagnostics_laboratory = 'PB' or diagnostics_laboratory = 'OPB'">
                                    <entry typeCode="COMP" contextConductionInd="true">

                                        <observation classCode="OBS" moodCode="EVN">
                                            <templateId root="1.2.276.0.76.10.4057"/>
                                            <id root="1.2.276.0.76.4.17.9814184919">
                                                <xsl:attribute name="extension">
                                                    <xsl:value-of select="concat(document_id, '-diag-08')"/>
                                                </xsl:attribute>
                                            </id>
                                            <code code="26436-6" codeSystem="2.16.840.1.113883.6.1"
                                                  displayName="Laboratory studies"/>
                                            <text>
                                                <reference value="#proc-8"/>
                                            </text>
                                            <statusCode code="completed"/>
                                            <effectiveTime value="201501171650">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="diagnostics_ts"/>
                                                </xsl:attribute>
                                            </effectiveTime>
                                            <value xsi:type="CE" codeSystem="1.2.276.0.76.3.1.195.5.51">
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="diagnostics_laboratory"/>
                                                </xsl:attribute>
                                            </value>
                                        </observation>
                                    </entry>
                                </xsl:when>
                            </xsl:choose>
                            <xsl:choose>
                                <xsl:when
                                        test="diagnostics_mrt = 'PB' or diagnostics_mrt = 'OPB'">
                                    <entry typeCode="COMP" contextConductionInd="true">

                                        <observation classCode="OBS" moodCode="EVN">
                                            <templateId root="1.2.276.0.76.10.4058"/>
                                            <id root="1.2.276.0.76.4.17.9814184919">
                                                <xsl:attribute name="extension">
                                                    <xsl:value-of select="concat(document_id, '-diag-09')"/>
                                                </xsl:attribute>
                                            </id>
                                            <code code="25056-3" codeSystem="2.16.840.1.113883.6.1"
                                                  displayName="Unspecified body region MRT"/>
                                            <text>
                                                <reference value="#proc-9"/>
                                            </text>
                                            <statusCode code="completed"/>
                                            <effectiveTime value="201501171650">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="diagnostics_ts"/>
                                                </xsl:attribute>
                                            </effectiveTime>
                                            <value xsi:type="CE" codeSystem="1.2.276.0.76.3.1.195.5.51">
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="diagnostics_mrt"/>
                                                </xsl:attribute>
                                            </value>
                                        </observation>
                                    </entry>
                                </xsl:when>
                            </xsl:choose>
                            <xsl:choose>
                                <xsl:when
                                        test="diagnostics_blood_gases = 'PB' or diagnostics_blood_gases = 'OPB'">
                                    <entry typeCode="COMP" contextConductionInd="true">

                                        <observation classCode="OBS" moodCode="EVN">
                                            <templateId root="1.2.276.0.76.10.4059"/>
                                            <id root="1.2.276.0.76.4.17.9814184919">
                                                <xsl:attribute name="extension">
                                                    <xsl:value-of select="concat(document_id, '-diag-10')"/>
                                                </xsl:attribute>
                                            </id>
                                            <code code="18767-4" codeSystem="2.16.840.1.113883.6.1"
                                                      displayName="Blood gas studies"/>
                                            <text>
                                                <reference value="#proc-10"/>
                                            </text>
                                            <statusCode code="completed"/>
                                            <effectiveTime value="201501171650">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="diagnostics_ts"/>
                                                </xsl:attribute>
                                            </effectiveTime>
                                            <value xsi:type="CE" codeSystem="1.2.276.0.76.3.1.195.5.51">
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="diagnostics_blood_gases"/>
                                                </xsl:attribute>
                                            </value>
                                        </observation>
                                    </entry>
                                </xsl:when>
                            </xsl:choose>
                            <xsl:choose>
                                <xsl:when
                                        test="diagnostics_urine_quick_test = 'PB' or diagnostics_urine_quick_test = 'OPB'">
                                    <entry typeCode="COMP" contextConductionInd="true">

                                        <observation classCode="OBS" moodCode="EVN">
                                            <templateId root="1.2.276.0.76.10.4060"/>
                                            <id root="1.2.276.0.76.4.17.9814184919">
                                                <xsl:attribute name="extension">
                                                    <xsl:value-of select="concat(document_id, '-diag-11')"/>
                                                </xsl:attribute>
                                            </id>
                                            <code code="50556-0" codeSystem="2.16.840.1.113883.6.1"
                                                  displayName="Urinalysis dipstick panel"/>
                                            <text>
                                                <reference value="#proc-11"/>
                                            </text>
                                            <statusCode code="completed"/>
                                            <effectiveTime value="201501171650">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="diagnostics_ts"/>
                                                </xsl:attribute>
                                            </effectiveTime>
                                            <value xsi:type="CE" codeSystem="1.2.276.0.76.3.1.195.5.51">
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="diagnostics_urine_quick_test"/>
                                                </xsl:attribute>
                                            </value>
                                        </observation>
                                    </entry>
                                </xsl:when>
                            </xsl:choose>
                            <xsl:choose>
                                <xsl:when
                                        test="diagnostics_ecg = 'PB' or diagnostics_ecg = 'OPB'">
                                    <entry typeCode="COMP" contextConductionInd="true">

                                        <observation classCode="OBS" moodCode="EVN">
                                            <templateId root="1.2.276.0.76.10.4061"/>
                                            <id root="1.2.276.0.76.4.17.9814184919">
                                                <xsl:attribute name="extension">
                                                    <xsl:value-of select="concat(document_id, '-diag-12')"/>
                                                </xsl:attribute>
                                            </id>
                                            <code code="34534-8" codeSystem="2.16.840.1.113883.6.1"
                                                  displayName="EKG 12 channel panel"/>
                                            <text>
                                                <reference value="#proc-12"/>
                                            </text>
                                            <statusCode code="completed"/>
                                            <effectiveTime value="201501171650">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="diagnostics_ts"/>
                                                </xsl:attribute>
                                            </effectiveTime>
                                            <value xsi:type="CE" codeSystem="1.2.276.0.76.3.1.195.5.51">
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="diagnostics_ecg"/>
                                                </xsl:attribute>
                                            </value>
                                        </observation>
                                    </entry>
                                </xsl:when>
                            </xsl:choose>
                            <xsl:choose>
                                <xsl:when
                                        test="diagnostics_ultrasound = 'PB' or diagnostics_ultrasound = 'OPB'">
                                    <entry typeCode="COMP" contextConductionInd="true">

                                        <observation classCode="OBS" moodCode="EVN">
                                            <templateId root="1.2.276.0.76.10.4062"/>
                                            <id root="1.2.276.0.76.4.17.9814184919">
                                                <xsl:attribute name="extension">
                                                    <xsl:value-of select="concat(document_id, '-diag-13')"/>
                                                </xsl:attribute>
                                            </id>
                                            <code code="25061-3" codeSystem="2.16.840.1.113883.6.1"
                                                  displayName="Unspecified body region US"/>
                                            <text>
                                                <reference value="#proc-13"/>
                                            </text>
                                            <statusCode code="completed"/>
                                            <effectiveTime value="201501171650">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="diagnostics_ts"/>
                                                </xsl:attribute>
                                            </effectiveTime>
                                            <value xsi:type="CE" codeSystem="1.2.276.0.76.3.1.195.5.51">
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="diagnostics_ultrasound"/>
                                                </xsl:attribute>
                                            </value>
                                        </observation>
                                    </entry>
                                </xsl:when>
                            </xsl:choose>
                            <xsl:choose>
                                <xsl:when
                                        test="diagnostics_ct_trauma = 'PB' or diagnostics_ct_trauma = 'OPB'">
                                    <entry typeCode="COMP" contextConductionInd="true">

                                        <observation classCode="OBS" moodCode="EVN">
                                            <templateId root="1.2.276.0.76.10.4063"/>
                                            <id root="1.2.276.0.76.4.17.9814184919">
                                                <xsl:attribute name="extension">
                                                    <xsl:value-of select="concat(document_id, '-diag-14')"/>
                                                </xsl:attribute>
                                            </id>
                                            <code code="25045-6" codeSystem="2.16.840.1.113883.6.1"
                                                  displayName="Unspecified body region CT"/>
                                            <text>
                                                <reference value="#proc-14"/>
                                            </text>
                                            <statusCode code="completed"/>
                                            <effectiveTime value="201501171650">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="diagnostics_ts"/>
                                                </xsl:attribute>
                                            </effectiveTime>
                                            <value xsi:type="CE" codeSystem="1.2.276.0.76.3.1.195.5.51">
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="diagnostics_ct_trauma"/>
                                                </xsl:attribute>
                                            </value>
                                        </observation>
                                    </entry>
                                </xsl:when>
                            </xsl:choose>
                            <xsl:choose>
                                <xsl:when
                                        test="diagnostics_echocardiographie = 'PB' or diagnostics_echocardiographie = 'OPB'">
                                    <entry typeCode="COMP" contextConductionInd="true">

                                        <observation classCode="OBS" moodCode="EVN">
                                            <templateId root="1.2.276.0.76.10.4064"/>
                                            <id root="1.2.276.0.76.4.17.9814184919">
                                                <xsl:attribute name="extension">
                                                    <xsl:value-of select="concat(document_id, '-diag-15')"/>
                                                </xsl:attribute>
                                            </id>
                                            <code code="42148-7" codeSystem="2.16.840.1.113883.6.1"
                                                  displayName="Heart US"/>
                                            <text>
                                                <reference value="#proc-15"/>
                                            </text>
                                            <statusCode code="completed"/>
                                            <effectiveTime value="201501171650">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="diagnostics_ts"/>
                                                </xsl:attribute>
                                            </effectiveTime>
                                            <value xsi:type="CE" codeSystem="1.2.276.0.76.3.1.195.5.51">
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="diagnostics_echocardiography"/>
                                                </xsl:attribute>
                                            </value>
                                        </observation>
                                    </entry>
                                </xsl:when>
                            </xsl:choose>
                        </section>
                    </component>

                    <!-- VitalSigns -->
                    <component typeCode="COMP" contextConductionInd="true">
                        <section classCode="DOCSECT">
                            <templateId root="1.2.276.0.76.10.3044"/>
                            <code code="8716-3" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
                                  displayName="Vital signs"/>
                            <title>Vitalparameter</title>
                            <text>&#160;</text>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4030"/>
                                    <id root="1.2.276.0.76.4.17.9814184919">
                                        <xsl:attribute name="extension">
                                            <xsl:value-of select="concat(document_id, '-resp')"/>
                                        </xsl:attribute>
                                    </id>
                                    <code code="9279-1" codeSystem="2.16.840.1.113883.6.1"
                                          displayName="Respiratory Rate">
                                        <originalText>Atemfrequenz</originalText>
                                    </code>
                                    <text>
                                        <reference value="#resp"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime>
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="vital_signs_ts"/>
                                        </xsl:attribute>
                                    </effectiveTime>
                                    <value xsi:type="PQ">
                                        <xsl:choose>
                                            <xsl:when test="respiratory_rate = ''">
                                                <xsl:attribute name="nullFlavor">UNK</xsl:attribute>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="respiratory_rate"/>
                                                </xsl:attribute>
                                                <xsl:attribute name="unit">/min</xsl:attribute>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </value>
                                </observation>
                            </entry>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4031"/>
                                    <id root="1.2.276.0.76.4.17.9814184919">
                                        <xsl:attribute name="extension">
                                            <xsl:value-of select="concat(document_id, '-oxy')"/>
                                        </xsl:attribute>
                                    </id>
                                    <code code="20564-1" codeSystem="2.16.840.1.113883.6.1"
                                          displayName="Oxygen saturation"/>
                                    <text>
                                        <reference value="#oxy"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime>
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="vital_signs_ts"/>
                                        </xsl:attribute>
                                    </effectiveTime>
                                    <value xsi:type="PQ">
                                        <xsl:choose>
                                            <xsl:when test="saturation = ''">
                                                <xsl:attribute name="nullFlavor">UNK</xsl:attribute>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="saturation"/>
                                                </xsl:attribute>
                                                <xsl:attribute name="unit">%</xsl:attribute>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </value>
                                </observation>
                            </entry>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4032"/>
                                    <id root="1.2.276.0.76.4.17.9814184919">
                                        <xsl:attribute name="extension">
                                            <xsl:value-of select="concat(document_id, '-sysbp')"/>
                                        </xsl:attribute>
                                    </id>
                                    <code code="8480-6" codeSystem="2.16.840.1.113883.6.1"
                                          displayName="Systolic blood pressure"/>
                                    <text>
                                        <reference value="#SysBP"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime>
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="vital_signs_ts"/>
                                        </xsl:attribute>
                                    </effectiveTime>
                                    <value xsi:type="PQ">
                                        <xsl:choose>
                                            <xsl:when test="blood_pressure_sys = ''">
                                                <xsl:attribute name="nullFlavor">UNK</xsl:attribute>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="blood_pressure_sys"/>
                                                </xsl:attribute>
                                                <xsl:attribute name="unit">mm[Hg]</xsl:attribute>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </value>
                                </observation>
                            </entry>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4033"/>
                                    <id root="1.2.276.0.76.4.17.9814184919">
                                        <xsl:attribute name="extension">
                                            <xsl:value-of select="concat(document_id, '-hr')"/>
                                        </xsl:attribute>
                                    </id>
                                    <code code="8867-4" codeSystem="2.16.840.1.113883.6.1" displayName="Heart Rate"/>
                                    <text>
                                        <reference value="#HeartR"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime>
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="vital_signs_ts"/>
                                        </xsl:attribute>
                                    </effectiveTime>
                                    <value xsi:type="PQ">
                                        <xsl:choose>
                                            <xsl:when test="heart_rate = ''">
                                                <xsl:attribute name="nullFlavor">UNK</xsl:attribute>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="heart_rate"/>
                                                </xsl:attribute>
                                                <xsl:attribute name="unit">/min</xsl:attribute>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </value>
                                </observation>
                            </entry>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4034"/>
                                    <id root="1.2.276.0.76.4.17.9814184919">
                                        <xsl:attribute name="extension">
                                            <xsl:value-of select="concat(document_id, '-gcs')"/>
                                        </xsl:attribute>
                                    </id>
                                    <code code="9269-2" codeSystem="2.16.840.1.113883.6.1"
                                          displayName="Glasgow coma score total"/>
                                    <text>
                                        <reference value="#GlasgowCS"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime>
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="vital_signs_ts"/>
                                        </xsl:attribute>
                                    </effectiveTime>
                                    <value xsi:type="PQ">
                                        <xsl:attribute name="value">
                                            <xsl:choose>
                                                <xsl:when test="gcs_total = ''">15</xsl:when>
                                                <xsl:otherwise><xsl:value-of select="gcs_total"/></xsl:otherwise>
                                            </xsl:choose>
                                        </xsl:attribute>
                                        <xsl:attribute name="unit">
                                            <xsl:text>{score}</xsl:text>
                                        </xsl:attribute>
                                    </value>
                                    <entryRelationship typeCode="COMP" contextConductionInd="true">
                                        <observation classCode="OBS" moodCode="EVN">
                                            <code code="9267-6" codeSystem="2.16.840.1.113883.6.1"
                                                  displayName="Glasgow coma score eye opening"/>
                                            <statusCode code="completed"/>
                                            <value xsi:type="PQ">
                                                <xsl:attribute name="value">
                                                    <xsl:choose>
                                                        <xsl:when test="gcs_eyes = ''">4</xsl:when>
                                                        <xsl:otherwise><xsl:value-of select="gcs_eyes"/></xsl:otherwise>
                                                    </xsl:choose>
                                                </xsl:attribute>
                                                <xsl:attribute name="unit">
                                                    <xsl:text>{score}</xsl:text>
                                                </xsl:attribute>
                                            </value>
                                        </observation>
                                    </entryRelationship>
                                    <entryRelationship typeCode="COMP" contextConductionInd="true">
                                        <observation classCode="OBS" moodCode="EVN">
                                            <code code="9270-0" codeSystem="2.16.840.1.113883.6.1"
                                                  displayName="Glasgow coma score verbal"/>
                                            <statusCode code="completed"/>
                                            <value xsi:type="PQ">
                                                <xsl:attribute name="value">
                                                    <xsl:choose>
                                                        <xsl:when test="gcs_verbal = ''">5</xsl:when>
                                                        <xsl:otherwise><xsl:value-of select="gcs_verbal"/></xsl:otherwise>
                                                    </xsl:choose>
                                                </xsl:attribute>
                                                <xsl:attribute name="unit">
                                                    <xsl:text>{score}</xsl:text>
                                                </xsl:attribute>
                                            </value>
                                        </observation>
                                    </entryRelationship>
                                    <entryRelationship typeCode="COMP" contextConductionInd="true">
                                        <observation classCode="OBS" moodCode="EVN">
                                            <code code="9268-4" codeSystem="2.16.840.1.113883.6.1"
                                                  displayName="Glasgow coma score motor"/>
                                            <statusCode code="completed"/>
                                            <value xsi:type="PQ">
                                                <xsl:attribute name="value">
                                                    <xsl:choose>
                                                        <xsl:when test="gcs_motor = ''">6</xsl:when>
                                                        <xsl:otherwise><xsl:value-of select="gcs_motor"/></xsl:otherwise>
                                                    </xsl:choose>
                                                </xsl:attribute>
                                                <xsl:attribute name="unit">
                                                    <xsl:text>{score}</xsl:text>
                                                </xsl:attribute>
                                            </value>
                                        </observation>
                                    </entryRelationship>
                                </observation>
                            </entry>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4046"/>
                                    <id root="1.2.276.0.76.4.17.9814184919">
                                        <xsl:attribute name="extension">
                                            <xsl:value-of select="concat(document_id, '-pupil-sl')"/>
                                        </xsl:attribute>
                                    </id>
                                    <code code="SPPL" codeSystem="1.2.276.0.76.3.1.195.5.1"
                                          displayName="Pupillenweite"/>
                                    <text>
                                        <reference value="#PupilLeft"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime>
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="vital_signs_ts"/>
                                        </xsl:attribute>
                                    </effectiveTime>

                                    <!-- <value xsi:type="CV" code="#PupilWL#" codeSystem="1.2.276.0.76.3.1.195.5.49" displayName="mittel"/>-->
                                    <value xsi:type="CV">
                                        <xsl:choose>
                                            <xsl:when test="pupil_size_left = ''">
                                                <xsl:attribute name="nullFlavor">
                                                    <xsl:text>UNK</xsl:text>
                                                </xsl:attribute>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="pupil_size_left"/>
                                                </xsl:attribute>
                                                <xsl:attribute name="codeSystem">
                                                    <xsl:text>1.2.276.0.76.3.1.195.5.49</xsl:text>
                                                </xsl:attribute>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </value>
                                    <targetSiteCode code="L" codeSystem="1.2.276.0.76.3.1.195.5.48"
                                                    displayName="Auge links"/>
                                </observation>
                            </entry>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4046"/>
                                    <id root="1.2.276.0.76.4.17.9814184919">
                                        <xsl:attribute name="extension">
                                            <xsl:value-of select="concat(document_id, '-pupil-sr')"/>
                                        </xsl:attribute>
                                    </id>
                                    <code code="SPPL" codeSystem="1.2.276.0.76.3.1.195.5.1"
                                          displayName="Pupillenweite"/>
                                    <text>
                                        <reference value="#PupilRight"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime>
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="vital_signs_ts"/>
                                        </xsl:attribute>
                                    </effectiveTime>
                                    <value xsi:type="CV">
                                        <xsl:choose>
                                            <xsl:when test="pupil_size_right = ''">
                                                <xsl:attribute name="nullFlavor">
                                                    <xsl:text>UNK</xsl:text>
                                                </xsl:attribute>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="pupil_size_right"/>
                                                </xsl:attribute>
                                                <xsl:attribute name="codeSystem">
                                                    <xsl:text>1.2.276.0.76.3.1.195.5.49</xsl:text>
                                                </xsl:attribute>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </value>
                                    <!--<value xsi:type="CV" code="#PupilWR#" codeSystem="1.2.276.0.76.3.1.195.5.49" displayName="mittel"/>-->
                                    <targetSiteCode code="R" codeSystem="1.2.276.0.76.3.1.195.5.48"
                                                    displayName="Auge rechts"/>
                                </observation>
                            </entry>

                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4047"/>
                                    <id root="1.2.276.0.76.4.17.9814184919">
                                        <xsl:attribute name="extension">
                                            <xsl:value-of select="concat(document_id, '-pupil-rl')"/>
                                        </xsl:attribute>
                                    </id>
                                    <code code="RPPL" codeSystem="1.2.276.0.76.3.1.195.5.1"
                                          displayName="Pupillenreaktion"/>
                                    <text>
                                        <reference value="#PupilLeft"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime>
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="vital_signs_ts"/>
                                        </xsl:attribute>
                                    </effectiveTime>

                                    <value xsi:type="CV">
                                        <xsl:choose>
                                            <xsl:when test="pupil_reaction_left = ''">
                                                <xsl:attribute name="nullFlavor">
                                                    <xsl:text>UNK</xsl:text>
                                                </xsl:attribute>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:attribute name="codeSystem">
                                                    <xsl:text>1.2.276.0.76.3.1.195.5.50</xsl:text>
                                                </xsl:attribute>
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="pupil_reaction_left"/>
                                                </xsl:attribute>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </value>
                                    <!--<value xsi:type="CV" code="#PupilRR#" codeSystem="1.2.276.0.76.3.1.195.5.50" displayName="prompt"/>-->
                                    <targetSiteCode code="L" codeSystem="1.2.276.0.76.3.1.195.5.48"
                                                    displayName="Auge links"/>
                                </observation>
                            </entry>

                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4047"/>
                                    <id root="1.2.276.0.76.4.17.9814184919">
                                        <xsl:attribute name="extension">
                                            <xsl:value-of select="concat(document_id, '-pupil-rr')"/>
                                        </xsl:attribute>
                                    </id>
                                    <code code="RPPL" codeSystem="1.2.276.0.76.3.1.195.5.1"
                                          displayName="Pupillenreaktion"/>
                                    <text>
                                        <reference value="#PupilRight"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime>
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="vital_signs_ts"/>
                                        </xsl:attribute>
                                    </effectiveTime>
                                    <value xsi:type="CV">
                                        <xsl:choose>
                                            <xsl:when test="pupil_reaction_right = ''">
                                                <xsl:attribute name="nullFlavor">
                                                    <xsl:text>UNK</xsl:text>
                                                </xsl:attribute>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:attribute name="codeSystem">
                                                    <xsl:text>1.2.276.0.76.3.1.195.5.50</xsl:text>
                                                </xsl:attribute>
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="pupil_reaction_right"/>
                                                </xsl:attribute>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </value>
                                    <!--<value xsi:type="CV" code="#PupilRL#" codeSystem="1.2.276.0.76.3.1.195.5.50" displayName="prompt"/>
                                    -->
                                    <targetSiteCode code="R" codeSystem="1.2.276.0.76.3.1.195.5.48"
                                                    displayName="Auge rechts"/>
                                </observation>
                            </entry>

                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4035"/>
                                    <id root="1.2.276.0.76.4.17.9814184919">
                                        <xsl:attribute name="extension">
                                            <xsl:value-of select="concat(document_id, '-temp')"/>
                                        </xsl:attribute>
                                    </id>
                                    <code code="8329-5" codeSystem="2.16.840.1.113883.6.1"
                                          displayName="Body temperature - Core"/>
                                    <text>
                                        <reference value="#BodyTemp"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime>
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="vital_signs_ts"/>
                                        </xsl:attribute>
                                    </effectiveTime>
                                    <value xsi:type="PQ">
                                        <xsl:attribute name="value">
                                            <xsl:choose>
                                                <xsl:when test="body_temperature = ''">37.0</xsl:when>
                                                <xsl:otherwise><xsl:value-of select="body_temperature"/></xsl:otherwise>
                                            </xsl:choose>
                                        </xsl:attribute>
                                        <xsl:attribute name="unit">Cel</xsl:attribute>
                                    </value>
                                </observation>
                            </entry>

                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4036"/>
                                    <id root="1.2.276.0.76.4.17.9814184919">
                                        <xsl:attribute name="extension">
                                            <xsl:value-of select="concat(document_id, '-pain')"/>
                                        </xsl:attribute>
                                    </id>
                                    <code code="72514-3" codeSystem="2.16.840.1.113883.6.1"
                                          displayName="Pain severity - 0-10 verbal numeric rating"/>
                                    <text>
                                        <reference value="#Pain"/>
                                    </text>
                                    <!-- 56840-2" Pain severity verbal numeric scale -->
                                    <statusCode code="completed"/>
                                    <effectiveTime>
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="vital_signs_ts"/>
                                        </xsl:attribute>
                                    </effectiveTime>
                                    <value xsi:type="PQ">
                                        <xsl:attribute name="value">
                                            <xsl:choose>
                                                <xsl:when test="pain_severity = ''">5</xsl:when>
                                                <xsl:otherwise><xsl:value-of select="pain_severity"/></xsl:otherwise>
                                            </xsl:choose>
                                        </xsl:attribute>
                                        <xsl:attribute name="unit">
                                            <xsl:text>{score}</xsl:text>
                                        </xsl:attribute>
                                    </value>
                                </observation>
                            </entry>
                        </section>
                    </component>


                    <!-- Allergien, Unverträglichkeiten -->
                    <component typeCode="COMP" contextConductionInd="true">
                        <section classCode="DOCSECT" moodCode="EVN">
                            <templateId root="1.2.276.0.76.10.3051"/>
                            <code code="48765-2" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
                                  displayName="Allergies &amp;or adverse reactions"/>
                            <title>Allergien und Unverträglichkeiten</title>
                            <text>
                                <xsl:choose>
                                    <xsl:when test="allergies_txt = ''">
                                        <xsl:text>&#160;</xsl:text>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:value-of select="allergies_txt"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </text>
                            <entry typeCode="COMP">
                                <act classCode="ACT" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4065"/>
                                    <id root="1.2.276.0.76.4.17.9814184919">
                                        <xsl:attribute name="extension">
                                            <xsl:value-of select="concat(document_id, '-alg-act')"/>
                                        </xsl:attribute>
                                    </id>
                                    <code code="CONC" codeSystem="2.16.840.1.113883.5.6"/>
                                    <statusCode code="active"/>
                                    <!-- This is the time stamp for when the allergy was first documented as a concern-->
                                    <effectiveTime>
                                        <low value="20150117"/>
                                    </effectiveTime>
                                    <entryRelationship typeCode="SUBJ">
                                        <!--Allergien allgemein-->
                                        <observation classCode="OBS" moodCode="EVN">
                                            <xsl:attribute name="negationInd">
                                                <xsl:value-of select="allergy"/>
                                            </xsl:attribute>
                                            <templateId root="1.2.276.0.76.10.4066"/>
                                            <id root="1.2.276.0.76.4.17.9814184919">
                                                <xsl:attribute name="extension">
                                                    <xsl:value-of select="concat(document_id, '-alg-gen')"/>
                                                </xsl:attribute>
                                            </id>
                                            <code code="ASSERTION" codeSystem="2.16.840.1.113883.5.4"/>
                                            <statusCode code="completed"/>
                                            <!-- N/A - author/time records when this assertion was made -->
                                            <effectiveTime nullFlavor="NA"/>
                                            <value xsi:type="CV" code="OINT" codeSystem="2.16.840.1.113883.5.4"
                                                   displayName="adverse reaction upon exposure to an agent"/>
                                            <participant typeCode="CSM">
                                                <participantRole classCode="MANU">
                                                    <playingEntity classCode="MMAT">
                                                        <code code="ALGN" codeSystem="1.2.276.0.76.3.1.195.5.52"
                                                              displayName="Allergen">
                                                            <originalText>
                                                                <reference value="#alg-4"/>
                                                            </originalText>
                                                        </code>
                                                    </playingEntity>
                                                </participantRole>
                                            </participant>
                                        </observation>
                                    </entryRelationship>
                                    <!--AntibiotikaAllergie-->
                                    <entryRelationship typeCode="SUBJ">
                                        <observation classCode="OBS" moodCode="EVN">
                                            <xsl:attribute name="negationInd">
                                                <xsl:value-of select="allergy_antibiotics"/>
                                            </xsl:attribute>
                                            <templateId root="1.2.276.0.76.10.4066"/>
                                            <id root="1.2.276.0.76.4.17.9814184919">
                                                <xsl:attribute name="extension">
                                                    <xsl:value-of select="concat(document_id, '-alg-atb')"/>
                                                </xsl:attribute>
                                            </id>
                                            <code code="ASSERTION" codeSystem="2.16.840.1.113883.5.4"/>
                                            <statusCode code="completed"/>
                                            <effectiveTime>
                                                <low value="2010"/>
                                            </effectiveTime>
                                            <value xsi:type="CV" code="OINT" codeSystem="2.16.840.1.113883.5.4"
                                                   displayName="adverse reaction upon exposure to an agent"/>
                                            <participant typeCode="CSM">
                                                <participantRole classCode="MANU">
                                                    <playingEntity classCode="MMAT">
                                                        <code code="A07AA" codeSystem="2.16.840.1.113883.6.73"
                                                              displayName="Antibiotikum">
                                                            <originalText>
                                                                <reference value="#alg-1"/>
                                                            </originalText>
                                                        </code>
                                                    </playingEntity>
                                                </participantRole>
                                            </participant>
                                        </observation>
                                    </entryRelationship>
                                    <!-- Kontrastmittel -->
                                    <entryRelationship typeCode="SUBJ">
                                        <observation classCode="OBS" moodCode="EVN">
                                            <xsl:attribute name="negationInd">
                                                <xsl:value-of select="allergy_contrast_agent"/>
                                            </xsl:attribute>
                                            <templateId root="1.2.276.0.76.10.4066"/>
                                            <id root="1.2.276.0.76.4.17.9814184919">
                                                <xsl:attribute name="extension">
                                                    <xsl:value-of select="concat(document_id, '-alg-kont')"/>
                                                </xsl:attribute>
                                            </id>
                                            <code code="ASSERTION" codeSystem="2.16.840.1.113883.5.4"/>
                                            <statusCode code="completed"/>
                                            <effectiveTime nullFlavor="NA"/>
                                            <value xsi:type="CV" code="OINT" codeSystem="2.16.840.1.113883.5.4"
                                                   displayName="adverse reaction upon exposure to an agent"/>
                                            <participant typeCode="CSM">
                                                <participantRole classCode="MANU">
                                                    <playingEntity classCode="MMAT">
                                                        <code code="V08" codeSystem="2.16.840.1.113883.6.73"
                                                              displayName="Kontrastmittel">
                                                            <originalText>
                                                                <reference value="#alg-2"/>
                                                            </originalText>
                                                        </code>
                                                    </playingEntity>
                                                </participantRole>
                                            </participant>
                                        </observation>
                                    </entryRelationship>
                                    <!-- Sonstige Allergien -->
                                    <entryRelationship typeCode="SUBJ">

                                        <observation classCode="OBS" moodCode="EVN">
                                            <xsl:attribute name="negationInd">
                                                <xsl:value-of select="allergy_other"/>
                                            </xsl:attribute>
                                            <templateId root="1.2.276.0.76.10.4066"/>
                                            <id root="1.2.276.0.76.4.17.9814184919">
                                                <xsl:attribute name="extension">
                                                    <xsl:value-of select="concat(document_id, '-alg-oth')"/>
                                                </xsl:attribute>
                                            </id>
                                            <code code="ASSERTION" codeSystem="2.16.840.1.113883.5.4"/>
                                            <statusCode code="completed"/>
                                            <effectiveTime nullFlavor="NA"/>
                                            <value xsi:type="CV" code="OINT" codeSystem="2.16.840.1.113883.5.4"
                                                   displayName="adverse reaction upon exposure to an agent"/>
                                            <participant typeCode="CSM">
                                                <participantRole classCode="MANU">
                                                    <playingEntity classCode="MMAT">
                                                        <code nullFlavor="OTH">
                                                            <originalText>
                                                                <reference value="#alg-4"/>
                                                            </originalText>
                                                        </code>
                                                    </playingEntity>
                                                </participantRole>
                                            </participant>
                                        </observation>
                                    </entryRelationship>
                                </act>
                            </entry>
                        </section>
                    </component>

                    <!-- Befunde / Verlauf / durchgeführte Therapie-->
                    <component typeCode="COMP" contextConductionInd="true">
                        <section classCode="DOCSECT">
                            <templateId root="1.2.276.0.76.10.3056"/>
                            <code code="67661-9" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
                                  displayName="EMS disposition"/>
                            <title>Weiteres Procedere / Therapieempfehlung / Weiterbehandler</title>
                            <text>
                                <list>
                                    <item ID="refact">Weiterbehandler: Hausarzt</item>
                                </list>
                            </text>
                            <xsl:if test="verlegung_type != ''">
                                <entry typeCode="COMP">
                                    <act classCode="ACT" moodCode="INT">
                                        <templateId root="1.2.276.0.76.10.4067"/>
                                        <code codeSystem="1.2.276.0.76.3.1.195.5.53">
                                            <xsl:attribute name="code">
                                                <xsl:value-of select="verlegung_type"/>
                                            </xsl:attribute>
                                        </code>
                                        <text>
                                            <reference value="#refact"/>
                                        </text>
                                    </act>
                                </entry>
                            </xsl:if>
                        </section>
                    </component>

                    <!-- Befunde / Verlauf / durchgeführte Therapie (section 3054) — only when isolation present -->
                    <xsl:if test="isolation_grund != ''">
                        <component typeCode="COMP" contextConductionInd="true">
                            <section classCode="DOCSECT">
                                <templateId root="1.2.276.0.76.10.3054"/>
                                <code code="67781-5" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
                                      displayName="Summarization of encounter note"/>
                                <title>Befunde / Verlauf / durchgeführte Therapie</title>
                                <text>
                                    <list>
                                        <item ID="iso">Isolation</item>
                                    </list>
                                </text>
                                <entry typeCode="COMP" contextConductionInd="true">
                                    <procedure classCode="PROC" moodCode="EVN">
                                        <templateId root="1.2.276.0.76.10.4068"/>
                                        <id root="1.2.276.0.76.4.17.9814184919">
                                            <xsl:attribute name="extension">
                                                <xsl:value-of select="concat(document_id, '-iso-proc')"/>
                                            </xsl:attribute>
                                        </id>
                                        <code code="ISO" codeSystem="1.2.276.0.76.3.1.195.5.54"
                                              displayName="Isolation"/>
                                        <text>
                                            <reference value="#iso"/>
                                        </text>
                                        <statusCode code="completed"/>
                                        <entryRelationship typeCode="RSON">
                                            <observation classCode="OBS" moodCode="EVN">
                                                <templateId root="1.2.276.0.76.10.4069"/>
                                                <id root="1.2.276.0.76.4.17.9814184919">
                                                    <xsl:attribute name="extension">
                                                        <xsl:value-of select="concat(document_id, '-iso-grund')"/>
                                                    </xsl:attribute>
                                                </id>
                                                <code code="44100-6" codeSystem="2.16.840.1.113883.6.1"
                                                      displayName="Medical Problem"/>
                                                <statusCode code="completed"/>
                                                <value xsi:type="CV">
                                                    <xsl:choose>
                                                        <xsl:when test="isolation_grund = 'OTH'">
                                                            <xsl:attribute name="nullFlavor">
                                                                <xsl:text>OTH</xsl:text>
                                                            </xsl:attribute>
                                                        </xsl:when>
                                                        <xsl:otherwise>
                                                            <xsl:attribute name="code">
                                                                <xsl:value-of select="isolation_grund"/>
                                                            </xsl:attribute>
                                                            <xsl:attribute name="codeSystem">
                                                                <xsl:text>2.16.840.1.113883.6.3</xsl:text>
                                                            </xsl:attribute>
                                                        </xsl:otherwise>
                                                    </xsl:choose>
                                                </value>
                                            </observation>
                                        </entryRelationship>
                                    </procedure>
                                </entry>
                            </section>
                        </component>
                    </xsl:if>

                    <!-- Abschlussdiagnosen -->
                    <component typeCode="COMP" contextConductionInd="true">
                        <section classCode="DOCSECT">
                            <templateId root="1.2.276.0.76.10.3055"/>
                            <code code="11301-9" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
                                  displayName="ED diagnosis"/>
                            <title>Abschlussdiagnosen</title>
                            <xsl:choose>
                                <xsl:when test="*[starts-with(name(), 'diagnosis_code') and . != ''][position() &lt;= 10]">
                                    <text>
                                        <list>
                                            <!-- One item per non-empty diagnosis code (max 10); ID matches the field suffix -->
                                            <xsl:for-each select="*[starts-with(name(), 'diagnosis_code') and . != ''][position() &lt;= 10]">
                                                <xsl:variable name="suffix" select="substring-after(name(), 'diagnosis_code_')"/>
                                                <xsl:variable name="diagName" select="../*[name() = concat('diagnosis_name_', $suffix)]"/>
                                                <item>
                                                    <xsl:attribute name="ID">
                                                        <xsl:value-of select="concat('diag-', $suffix)"/>
                                                    </xsl:attribute>
                                                    <xsl:choose>
                                                        <xsl:when test="$diagName != ''">
                                                            <xsl:value-of select="concat(., ' ', $diagName)"/>
                                                        </xsl:when>
                                                        <xsl:otherwise>
                                                            <xsl:value-of select="."/>
                                                        </xsl:otherwise>
                                                    </xsl:choose>
                                                </item>
                                            </xsl:for-each>
                                        </list>
                                    </text>
                                </xsl:when>
                                <xsl:otherwise>
                                    <text/>
                                </xsl:otherwise>
                            </xsl:choose>
                            <xsl:if test="*[starts-with(name(), 'diagnosis_code') and . != ''][position() &lt;= 10]">
                            <entry typeCode="COMP">
                                <act classCode="ACT" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4048"/>
                                    <id root="1.2.276.0.76.4.17.9814184919">
                                        <xsl:attribute name="extension">
                                            <xsl:value-of select="concat(document_id, '-diag-act')"/>
                                        </xsl:attribute>
                                    </id>
                                    <code code="CONC" codeSystem="2.16.840.1.113883.5.6" displayName="Concern"/>
                                    <statusCode code="active"/>
                                    <effectiveTime>
                                        <low>
                                            <xsl:attribute name="value">
                                                <xsl:value-of select="admission_ts"/>
                                            </xsl:attribute>
                                        </low>
                                    </effectiveTime>
                                    <!-- Iterate over diagnosis codes max 10; skip empty; position 1 is leading -->
                                    <xsl:variable name="doc_id" select="document_id"/>
                                    <xsl:for-each select="*[starts-with(name(), 'diagnosis_code') and . != ''][position() &lt;= 10]">
                                        <xsl:variable name="position" select="position()"/>
                                        <xsl:variable name="suffix" select="substring-after(name(), 'diagnosis_code_')"/>
                                        <entryRelationship typeCode="SUBJ">
                                            <xsl:if test="$position = 1">
                                                <sequenceNumber value="1"/>
                                            </xsl:if>
                                            <observation classCode="OBS" moodCode="EVN">
                                                <templateId root="1.2.276.0.76.10.4049"/>
                                                <id root="1.2.276.0.76.4.17.9814184919">
                                                    <xsl:attribute name="extension">
                                                        <xsl:value-of select="concat($doc_id, '-diag-obs-', $suffix)"/>
                                                    </xsl:attribute>
                                                </id>
                                                <code code="29308-4" codeSystem="2.16.840.1.113883.6.1"
                                                      displayName="Diagnosis"/>
                                                <text>
                                                    <reference value="#diag-{$suffix}"/>
                                                </text>
                                                <statusCode code="completed"/>
                                                <effectiveTime>
                                                    <low>
                                                        <xsl:attribute name="value">
                                                            <xsl:value-of select="../admission_ts"/>
                                                        </xsl:attribute>
                                                    </low>
                                                </effectiveTime>
                                                <value xsi:type="CD">
                                                    <xsl:choose>
                                                        <xsl:when test=". = 'OTH'">
                                                            <xsl:attribute name="nullFlavor">
                                                                <xsl:text>OTH</xsl:text>
                                                            </xsl:attribute>
                                                        </xsl:when>
                                                        <xsl:otherwise>
                                                            <xsl:attribute name="code">
                                                                <xsl:value-of select="."/>
                                                            </xsl:attribute>
                                                            <xsl:attribute name="codeSystem">
                                                                <xsl:text>1.2.276.0.76.5.424</xsl:text>
                                                            </xsl:attribute>
                                                            <xsl:attribute name="codeSystemName">
                                                                <xsl:text>icd10gm2015</xsl:text>
                                                            </xsl:attribute>
                                                        </xsl:otherwise>
                                                    </xsl:choose>
                                                    <originalText>
                                                        <xsl:variable name="correspondingName"
                                                                      select="../*[name() = concat('diagnosis_name_', $suffix)]"/>
                                                        <xsl:choose>
                                                            <xsl:when test="$correspondingName = ''">
                                                                <xsl:attribute name="nullFlavor">
                                                                    <xsl:text>UNK</xsl:text>
                                                                </xsl:attribute>
                                                            </xsl:when>
                                                            <xsl:otherwise>
                                                                <xsl:value-of select="$correspondingName"/>
                                                            </xsl:otherwise>
                                                        </xsl:choose>
                                                    </originalText>
                                                    <xsl:variable name="correspondingQualifier"
                                                                  select="../*[name() = concat('diagnosis_qualifier_', $suffix)]"/>
                                                    <xsl:if test="$correspondingQualifier != ''">
                                                        <qualifier>
                                                            <name code="8"
                                                                  codeSystem="2.16.840.1.113883.3.7.1.0"/>
                                                            <value xsi:type="CV" codeSystem="1.2.276.0.76.3.1.1.5.1.21">
                                                                <xsl:attribute name="code">
                                                                    <xsl:value-of select="$correspondingQualifier"/>
                                                                </xsl:attribute>
                                                            </value>
                                                        </qualifier>
                                                    </xsl:if>
                                                </value>
                                            </observation>
                                        </entryRelationship>
                                    </xsl:for-each>
                                </act>
                            </entry>
                            </xsl:if>
                        </section>
                    </component>
                </structuredBody>
            </component>
        </ClinicalDocument>
    </xsl:template>
</xsl:stylesheet>