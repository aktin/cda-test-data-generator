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
                    <xsl:value-of select="dokument_id"/>
                </xsl:attribute>
            </id>
            <!-- Fixer Dokumententype-Code -->
            <code code="68552-9" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
                  displayName="Emergency medicine Emergency department Admission evaluation note"/>
            <!-- Datum und Zeit der Erstellung -->
            <effectiveTime>
                <xsl:attribute name="value">
                    <xsl:value-of select="datum_erstellung"/>
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
                        <postalCode>
                            <xsl:value-of select="postleitzahl"/>
                        </postalCode>
                        <city>
                            <xsl:value-of select="city"/>
                        </city>
                    </addr>
                    <patient classCode="PSN" determinerCode="INSTANCE">
                        <!-- Name -->
                        <name>
                            <given>
                                <xsl:value-of select="given_patient"/>
                            </given>
                            <family>
                                <xsl:value-of select="family_patient"/>
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
                                <xsl:value-of select="geburtsdatum_ts"/>
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
                    <id root="1.2.276.0.76.3.2.123456789"/>
                    <assignedPerson classCode="PSN" determinerCode="INSTANCE">
                        <name>
                            <prefix>
                                <xsl:value-of select="prefix_author"/>
                            </prefix>
                            <given>
                                <xsl:value-of select="given_author"/>
                            </given>
                            <family>
                                <xsl:value-of select="family_author"/>
                            </family>
                        </name>
                    </assignedPerson>
                    <representedOrganization classCode="ORG" determinerCode="INSTANCE">
                        <id root="1.2.276.0.76.4.17">
                            <xsl:attribute name="extension">
                                <xsl:value-of select="organisation_id"/>
                            </xsl:attribute>
                        </id>
                        <name>
                            <xsl:value-of select="organisation_name"/>
                        </name>
                    </representedOrganization>
                </assignedAuthor>
            </author>
            <!-- Verwaltungsorganisation des Dokuments -->
            <custodian>
                <assignedCustodian>
                    <representedCustodianOrganization>
                        <id root="1.2.276.0.76.4.17">
                            <xsl:attribute name="extension">
                                <xsl:value-of select="organisation_id"/>
                            </xsl:attribute>
                        </id>
                        <name>
                            <xsl:value-of select="organisation_name"/>
                        </name>
                    </representedCustodianOrganization>
                </assignedCustodian>
            </custodian>
            <!-- Kostenträger/Versicherung -->


            <participant typeCode="HLD">
                <templateId root="1.2.276.0.76.10.2022"/>
                <time>
                    <high value="20231231"/>  <!-- Hier muss immer ein Quartalsende angegeben (MM/JJ) => YYYYMMDD. -->
                </time>
                <associatedEntity classCode="POLHOLD">
                    <!-- eGK Nummer -->
                    <id extension="A123456789" root="1.2.276.0.76.4.8"/>
                    <!-- Versicherungsnummer -->
                    <id extension="123456789" root="1.2.276.0.76.3.1.131.1.4.3.9999.9999.999955"/>
                    <code code="SELF" codeSystem="2.16.840.1.113883.5.111" displayName="self">
                        <xsl:attribute name="code">
                            <xsl:value-of select="insurance_case"/>
                        </xsl:attribute>
                    </code>
                    <xsl:if test="insurance_case = 'FAMDEP'">
                        <associatedPerson>
                            <name>
                                <given>
                                    <xsl:value-of select="_associatedPerson_given"/>
                                </given>
                                <family>
                                    <xsl:value-of select="_associatedPerson_family"/>
                                </family>
                            </name>
                        </associatedPerson>
                    </xsl:if>
                    <scopingOrganization>
                        <!-- IK-NR -->
                        <id extension="987654321" root="1.2.276.0.76.4.5">
                            <xsl:attribute name="extension">
                                <xsl:value-of select="versicherung_iknr"/>
                            </xsl:attribute>
                        </id>
                        <!-- VK-NR -->
                        <id extension="3333" root="1.2.276.0.76.4.7"/>
                        <name>
                            <xsl:value-of select="versicherung_txt"/>
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
                                <xsl:value-of select="therapiebeginn_ts"/>
                            </xsl:attribute>
                        </low>
                        <!-- Verlegungs-/Entlassungszeitpunkt (Datum und Zeit), Zeitangabe genau bis auf die Minute-->
                        <high>
                            <xsl:attribute name="value">
                                <xsl:value-of select="entlassung_ts"/>
                            </xsl:attribute>
                        </high>
                    </effectiveTime>
                    <performer typeCode="PRF">
                        <!-- Erster Arzt, Arztkontakt Beginn und Ende -->
                        <time>
                            <!-- Begin des Arztkontaktes -->
                            <low>
                                <xsl:attribute name="value">
                                    <xsl:value-of select="arztkontakt_ts"/>
                                </xsl:attribute>
                            </low>
                            <!-- Ende des Arztkontaktes -->
                            <high>
                                <xsl:attribute name="value">
                                    <xsl:value-of select="end_arztkontakt_ts"/>
                                </xsl:attribute>
                            </high>
                        </time>
                        <assignedEntity classCode="ASSIGNED">
                            <id nullFlavor="NA"/>
                        </assignedEntity>
                    </performer>
                </serviceEvent>
            </documentationOf>
            <!-- Patientenkontakt -->
            <componentOf>
                <encompassingEncounter classCode="ENC" moodCode="EVN">
                    <!-- Aufnahme-Identifikator -->
                    <id root="1.2.276.0.76.3.87686">
                        <xsl:attribute name="extension">
                            <xsl:value-of select="encounter_id"/>
                        </xsl:attribute>
                    </id>
                    <effectiveTime>
                        <!-- Start Patientenkontakt -->
                        <low>
                            <xsl:attribute name="value">
                                <xsl:value-of select="aufnahme_ts"/>
                            </xsl:attribute>
                        </low>
                        <!-- Ende Patientenkontakt = Zeitpunkt der Verlegung/Entlassung -->
                        <high>
                            <xsl:attribute name="value">
                                <xsl:value-of select="entlassung_ts"/>
                            </xsl:attribute>
                        </high>
                    </effectiveTime>
                    <!-- Entlassung des Patienten mit Entlassungsgrund -->
                    <dischargeDispositionCode code="4" codeSystem="1.2.276.0.76.3.1.195.5.56">
                        <xsl:attribute name="code">
                            <xsl:value-of select="entlassung"/>
                        </xsl:attribute>
                    </dischargeDispositionCode>
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
                            <text>

                            </text>
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
                                                <xsl:value-of select="aufnahme_ts"/>
                                            </xsl:attribute>
                                        </high>
                                    </effectiveTime>
                                    <value xsi:type="CV" codeSystem="1.2.276.0.76.3.1.195.5.41">
                                        <xsl:attribute name="code">
                                            <xsl:value-of select="transportmittel"/>
                                        </xsl:attribute>

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
                                            <code codeSystem="1.2.276.0.76.5.440">
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="zuweisung"/>
                                                </xsl:attribute>
                                            </code>
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
                                <xsl:value-of select="notfallanamnese"/>
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
                                    <xsl:value-of select="beschwerde_liste"/>
                                </content>
                            </text>
                            <entry typeCode="COMP">
                                <act classCode="ACT" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4039"/>
                                    <id root="1.2.276.0.76.4.17.9814184919"
                                        extension="c7a7f896-6125-4de4-ab16-706f1d2221c1"/>
                                    <code code="CONC" codeSystem="2.16.840.1.113883.5.6" displayName="Concern"/>
                                    <statusCode code="active"/>
                                    <effectiveTime>
                                        <low>
                                            <xsl:attribute name="value">
                                                <xsl:value-of select="beschwerde_begin"/>
                                            </xsl:attribute>
                                        </low>
                                    </effectiveTime>
                                    <entryRelationship typeCode="SUBJ">
                                        <observation classCode="OBS" moodCode="EVN">
                                            <templateId root="1.2.276.0.76.10.4040"/>
                                            <id root="1.2.276.0.76.4.17.9814184919" extension="___?___"/>
                                            <code code="75322-8" codeSystem="2.16.840.1.113883.6.1"
                                                  displayName="Complaint"/>
                                            <text>
                                                <reference value="#compl-1"/>
                                            </text>
                                            <statusCode code="completed"/>
                                            <effectiveTime>
                                                <width value="1" unit="h">
                                                    <xsl:attribute name="value">
                                                        <xsl:value-of select="symptomdauer"/>
                                                    </xsl:attribute>
                                                </width>
                                            </effectiveTime>
                                            <value xsi:type="CE" codeSystem="1.2.276.0.76.5.439">
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="cedis"/>
                                                </xsl:attribute>
                                                <originalText>
                                                    <xsl:value-of select="beschwerden_txt"/>
                                                </originalText>
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
                                <xsl:value-of select="ersteinschaetzung_text"/>
                            </text>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4042"/>
                                    <id root="45F99818-637B-4BE7-BC22-A7041C1CF813">
                                    </id>
                                    <code code="11283-9" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
                                          displayName="Acuity assessment"/>
                                    <text>
                                        <reference value="#triage"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime>
                                        <low value="202006201603">
                                            <xsl:attribute name="value">
                                                <xsl:value-of select="triage_ts_start"/>
                                            </xsl:attribute>
                                        </low>
                                        <high value="202006201608">
                                            <xsl:attribute name="value">
                                                <xsl:value-of select="triage_ts_end"/>
                                            </xsl:attribute>
                                        </high>
                                    </effectiveTime>
                                    <value code="1" codeSystem="1.2.276.0.76.5.438" xsi:type="CE">
                                        <xsl:attribute name="code">
                                            <xsl:value-of select="triage"/>
                                        </xsl:attribute>
                                        <xsl:attribute name="codeSystem">
                                            <xsl:value-of select="triage_system"/>
                                        </xsl:attribute>
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


                                ||Schwanger:|<xsl:value-of select="schwanger_name"/>|
                                ||Tetanusschutz:|<xsl:value-of select="tetanusschutz_text"/>|

                                ||Rankin Skala Score:|<xsl:value-of select="rankin"/>|

                                |Multi|
                                <xsl:value-of select="keime"/>
                                |Multi|
                                |Verdacht|CONF|Verdacht|


                            </text>

                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4043"/>
                                    <id root="b2e0e192-416a-4e9c-97ce-2f3e27424242"/>
                                    <code code="11449-6" codeSystem="2.16.840.1.113883.6.1"
                                          displayName="Pregnancy status"/>
                                    <text>
                                        <reference value="#Preg"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime value="202006201545"/>
                                    <value code="1" codeSystem="1.2.276.0.76.3.1.195.5.46" xsi:type="CV">
                                        <xsl:attribute name="code">
                                            <xsl:value-of select="schwangerschaft"/>
                                        </xsl:attribute>
                                    </value>
                                    <!-- <value xsi:type="CV" code="#Pregnancy#" codeSystem="1.2.276.0.76.3.1.195.5.46" displayName="Patient nicht schwanger"/>-->
                                </observation>
                            </entry>

                            <entry typeCode="COMP" contextConductionInd="true">
                                <substanceAdministration moodCode="EVN" classCode="SBADM" negationInd="true">
                                    <xsl:attribute name="negationInd">
                                        <xsl:value-of select="tetanusschutz"/>
                                    </xsl:attribute>
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
                                    <id root="10C1EB7E-DC2D-4D1F-806A-2AD65EBA0396"/>
                                    <code code="75859-9" codeSystem="2.16.840.1.113883.6.1"
                                          displayName="Modified Rankin scale"/>
                                    <text>
                                        <reference value="#rankin"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime value="20200620"/>
                                    <value xsi:type="PQ" value="2" unit="{score}"
                                           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="rankin"/>
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
                                    <id root="1.2.276.0.76.4.17.9814184919"
                                        extension="dd8a6ff8-ed4b-4f7e-82c3-e98e58b45de6"/>
                                    <code code="CONC" codeSystem="2.16.840.1.113883.5.6" displayName="Concern"/>
                                    <statusCode code="completed"/>
                                    <effectiveTime>
                                        <low value="20150304"/>
                                    </effectiveTime>
                                    <entryRelationship typeCode="SUBJ">
                                        <observation classCode="OBS" moodCode="EVN">
                                            <templateId root="1.2.276.0.76.10.4073"/>
                                            <id root="1.2.276.0.76.4.17.9814184919"
                                                extension="3564b7c0-2111-43f2-a784-9a5fdfaa67f2"/>
                                            <code code="COND" codeSystem="2.16.840.1.113883.5.4"
                                                  displayName="Condition"/>
                                            <text>
                                                <reference value="#mdro-1"/>
                                            </text>
                                            <statusCode code="completed"/>
                                            <effectiveTime>
                                                <low value="20150304"/>
                                            </effectiveTime>
                                            <value code="3MRGN" codeSystem="1.2.276.0.76.5.441" xsi:type="CD">
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="keime"/>
                                                </xsl:attribute>
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
                                    <item ID="proc-4">
                                        <xsl:value-of select="diagnostik_text"/>
                                    </item>
                                </list>
                            </text>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4053">
                                        <xsl:attribute name="root">
                                            <xsl:value-of select="_diagnostik_id"/>
                                        </xsl:attribute>
                                    </templateId>
                                    <id root="1.2.276.0.76.4.17.9814184919"
                                        extension="944cd73e-4361-4fca-929b-9a404b063651"/>
                                    <code code="37637-6" codeSystem="2.16.840.1.113883.6.1"
                                          displayName="Extremity X-ray">
                                        <xsl:attribute name="code">
                                            <xsl:value-of select="diagnostik_code"/>
                                        </xsl:attribute>
                                        <xsl:attribute name="displayName">
                                            <xsl:value-of select="diagnostik_display_name"/>
                                        </xsl:attribute>

                                    </code>
                                    <text>
                                        <reference value="#proc-4"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime value="201501171650">
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="diagnostik_ts"/>
                                        </xsl:attribute>
                                    </effectiveTime>
                                    <value xsi:type="CE" code="OPB" codeSystem="1.2.276.0.76.3.1.195.5.51"
                                           displayName="ohne path. Befund">
                                        <xsl:attribute name="code">
                                            <xsl:value-of select="diagnostik_ergebnis_code"/>
                                        </xsl:attribute>
                                    </value>
                                    <xsl:choose>
                                        <xsl:when test="number(substring-after(_diagnostik_id, '1.2.276.0.76.10.')) > 4049 and
                                                        number(substring-after(_diagnostik_id, '1.2.276.0.76.10.')) &lt; 4057">
                                            <participant typeCode="LOC">
                                                <participantRole classCode="SDLOC">
                                                    <code code="ER" codeSystem="2.16.840.1.113883.5.111"
                                                          displayName="Notaufnahme"/>
                                                </participantRole>
                                            </participant>
                                        </xsl:when>
                                    </xsl:choose>
                                </observation>
                            </entry>
                        </section>
                    </component>

                    <!-- VitalSigns -->
                    <component typeCode="COMP" contextConductionInd="true">
                        <section classCode="DOCSECT">
                            <templateId root="1.2.276.0.76.10.3044"/>
                            <code code="8716-3" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
                                  displayName="Vital signs"/>
                            <title>Vitalparameter</title>
                            <text>
                            </text>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4030"/>
                                    <id root="10C1EB7E-DC2D-4D1F-806A-2AD65EBA0396"/>
                                    <code code="9279-1" codeSystem="2.16.840.1.113883.6.1"
                                          displayName="Respiratory Rate">
                                        <originalText>
                                            RR #AF#/Min
                                        </originalText>
                                    </code>
                                    <text>
                                        <reference value="#resp"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime value="20200620"/>
                                    <value xsi:type="PQ" value="54" unit="/min">
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="atemfrequenz"/>
                                        </xsl:attribute>
                                    </value>
                                </observation>
                            </entry>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4031"/>
                                    <id root="769eb111-93b0-4c84-8e55-98f2098b7950"/>
                                    <code code="20564-1" codeSystem="2.16.840.1.113883.6.1"
                                          displayName="Oxygen saturation"/>
                                    <text>
                                        <reference value="#oxy"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime value="20200620"/>
                                    <value xsi:type="PQ" value="88" unit="%">
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="saettigung"/>
                                        </xsl:attribute>
                                    </value>
                                </observation>
                            </entry>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4032"/>
                                    <id root="adeb672e-a620-4aa4-9117-bdd8b2505a78"/>
                                    <code code="8480-6" codeSystem="2.16.840.1.113883.6.1"
                                          displayName="Systolic blood pressure"/>
                                    <text>
                                        <reference value="#SysBP"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime value="20200620"/>
                                    <value xsi:type="PQ" value="174" unit="mm[Hg]">
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="blutdruck_sys"/>
                                        </xsl:attribute>
                                    </value>
                                </observation>
                            </entry>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4033"/>
                                    <id root="BBFB672E-A620-4AA4-9117-BDD8B2505AAA"/>
                                    <code code="8867-4" codeSystem="2.16.840.1.113883.6.1" displayName="Heart Rate"/>
                                    <text>
                                        <reference value="#HeartR"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime value="20200620"/>
                                    <value xsi:type="PQ" value="174" unit="/min">
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="herzfrequenz"/>
                                        </xsl:attribute>
                                    </value>
                                </observation>
                            </entry>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4034"/>
                                    <id root="98c1eb7e-dc2d-4d1f-806a-2ad65eba0351"/>
                                    <code code="9269-2" codeSystem="2.16.840.1.113883.6.1"
                                          displayName="Glasgow coma score total"/>
                                    <text>
                                        <reference value="#GlasgowCS"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime value="20200620"/>
                                    <value xsi:type="PQ" value="9" unit="{score}">
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="gcs_summe"/>
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
                                            <value xsi:type="PQ" value="2" unit="{score}">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="gcs_augen"/>
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
                                            <value xsi:type="PQ" value="1" unit="{score}">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="gcs_verbal"/>
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
                                            <value xsi:type="PQ" value="6" unit="{score}">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="gcs_motorisch"/>
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
                                    <id root="DEEE672E-A620-4AA4-9117-BDD8B2505AAF"/>
                                    <code code="SPPL" codeSystem="1.2.276.0.76.3.1.195.5.1"
                                          displayName="Pupillenweite"/>
                                    <text>
                                        <reference value="#PupilLeft"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime value="20200620"/>

                                    <!-- <value xsi:type="CV" code="#PupilWL#" codeSystem="1.2.276.0.76.3.1.195.5.49" displayName="mittel"/>-->
                                    <value code="C" codeSystem="1.2.276.0.76.3.1.195.5.49" xsi:type="CV"
                                           displayName="eng">
                                        <xsl:attribute name="code">
                                            <xsl:value-of select="pupillenweite_links"/>
                                        </xsl:attribute>
                                    </value>
                                    <targetSiteCode code="L" codeSystem="1.2.276.0.76.3.1.195.5.48"
                                                    displayName="Auge links"/>
                                </observation>
                            </entry>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4046"/>
                                    <id root="DEEE672E-A620-4AA4-9117-BDD8B2505AAF"/>
                                    <code code="SPPL" codeSystem="1.2.276.0.76.3.1.195.5.1"
                                          displayName="Pupillenweite"/>
                                    <text>
                                        <reference value="#PupilRight"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime value="20200620"/>
                                    <value code="D" codeSystem="1.2.276.0.76.3.1.195.5.49" xsi:type="CV"
                                           displayName="weit">
                                        <xsl:attribute name="code">
                                            <xsl:value-of select="pupillenweite_rechts"/>
                                        </xsl:attribute>
                                    </value>
                                    <!--<value xsi:type="CV" code="#PupilWR#" codeSystem="1.2.276.0.76.3.1.195.5.49" displayName="mittel"/>-->
                                    <targetSiteCode code="R" codeSystem="1.2.276.0.76.3.1.195.5.48"
                                                    displayName="Auge rechts"/>
                                </observation>
                            </entry>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4047"/>
                                    <id root="DEEE672E-A620-4AA4-9117-BDD8B2505AAF"/>
                                    <code code="RPPL" codeSystem="1.2.276.0.76.3.1.195.5.1"
                                          displayName="Pupillenreaktion"/>
                                    <text>
                                        <reference value="PupilLeft"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime value="20200620"/>
                                    <value code="D" codeSystem="1.2.276.0.76.3.1.195.5.50" xsi:type="CV">
                                        <xsl:attribute name="code">
                                            <xsl:value-of select="pupillenreaktion_rechts"/>
                                        </xsl:attribute>
                                    </value>
                                    <!--<value xsi:type="CV" code="#PupilRL#" codeSystem="1.2.276.0.76.3.1.195.5.50" displayName="prompt"/>
                                    -->
                                    <targetSiteCode code="L" codeSystem="1.2.276.0.76.3.1.195.5.48"
                                                    displayName="Auge links"/>
                                </observation>
                            </entry>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4047"/>
                                    <id root="DEEE672E-A620-4AA4-9117-BDD8B2505AAF"/>
                                    <code code="RPPL" codeSystem="1.2.276.0.76.3.1.195.5.1"
                                          displayName="Pupillenreaktion"/>
                                    <text>
                                        <reference value="PupilRight"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime value="20200620"/>

                                    <value code="B" codeSystem="1.2.276.0.76.3.1.195.5.50" xsi:type="CV"
                                           displayName="prompt">
                                        <xsl:attribute name="code">
                                            <xsl:value-of select="pupillenreaktion_links"/>
                                        </xsl:attribute>
                                    </value>
                                    <!--<value xsi:type="CV" code="#PupilRR#" codeSystem="1.2.276.0.76.3.1.195.5.50" displayName="prompt"/>-->
                                    <targetSiteCode code="R" codeSystem="1.2.276.0.76.3.1.195.5.48"
                                                    displayName="Auge rechts"/>
                                </observation>
                            </entry>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4035"/>
                                    <id root="AF1EB111-93B0-4C84-8E55-98F2098B7950"/>
                                    <code code="8329-5" codeSystem="2.16.840.1.113883.6.1"
                                          displayName="Body temperature - Core"/>
                                    <text>
                                        <reference value="#BodyTemp"/>
                                    </text>
                                    <statusCode code="completed"/>
                                    <effectiveTime value="20200620"/>
                                    <value xsi:type="PQ" value="0.425" unit="Cel">
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="kerntemperatur"/>
                                        </xsl:attribute>
                                    </value>
                                </observation>
                            </entry>
                            <entry typeCode="COMP" contextConductionInd="true">
                                <observation classCode="OBS" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4036"/>
                                    <id root="10C1EB7E-DC2D-4D1F-806A-2AD65EBA0396"/>
                                    <code code="72514-3" codeSystem="2.16.840.1.113883.6.1"
                                          displayName="Pain severity - 0-10 verbal numeric rating"/>
                                    <text>
                                        <reference value="#Pain"/>
                                    </text>
                                    <!-- 56840-2" Pain severity verbal numeric scale -->
                                    <statusCode code="completed"/>
                                    <effectiveTime value="20200620"/>
                                    <value xsi:type="PQ" value="9" unit="{score}">
                                        <xsl:attribute name="value">
                                            <xsl:value-of select="schmerzskala"/>
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
                                <xsl:value-of select="allergien_txt"/>
                            </text>
                            <entry typeCode="COMP">
                                <act classCode="ACT" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4065"/>
                                    <id root="1.2.276.0.76.4.17.9814184919"
                                        extension="15100194-6d6e-4b00-a4d8-effeb66596b4"/>
                                    <code code="CONC" codeSystem="2.16.840.1.113883.5.6"/>
                                    <statusCode code="active"/>
                                    <!-- This is the time stamp for when the allergy was first documented as a concern-->
                                    <effectiveTime>
                                        <low value="20150117"/>
                                    </effectiveTime>
                                    <entryRelationship typeCode="SUBJ">
                                        <!--Allergien allgemein-->
                                        <observation classCode="OBS" moodCode="EVN" negationInd="true">
                                            <xsl:attribute name="negationInd">
                                                <xsl:value-of select="allergie"/>
                                            </xsl:attribute>
                                            <templateId root="1.2.276.0.76.10.4066"/>
                                            <id root="1.2.276.0.76.4.17.9814184919"
                                                extension="c9599ec1-6077-4f74-b58e-80c4148efbd8"/>
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
                                                <xsl:value-of select="allergie_antibiotika"/>
                                            </xsl:attribute>
                                            <templateId root="1.2.276.0.76.10.4066"/>
                                            <id root="1.2.276.0.76.4.17.9814184919"
                                                extension="4adc1020-7b14-11db-9fe1-0800200c9a66"/>
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
                                        <observation classCode="OBS" moodCode="EVN" negationInd="true">
                                            <xsl:attribute name="negationInd">
                                                <xsl:value-of select="allergie_kontrastmittel"/>
                                            </xsl:attribute>
                                            <templateId root="1.2.276.0.76.10.4066"/>
                                            <id root="1.2.276.0.76.4.17.9814184919"
                                                extension="4adc1020-7b14-11db-9fe1-0800200c9a66"/>
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
                                                <xsl:value-of select="allergie_sonstige"/>
                                            </xsl:attribute>
                                            <templateId root="1.2.276.0.76.10.4066"/>
                                            <id root="1.2.276.0.76.4.17.9814184919"
                                                extension="4adc1020-7b14-11db-9fe1-0800200c9a66"/>
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
                        </section>
                    </component>

                    <!-- Abschlussdiagnosen -->
                    <component typeCode="COMP" contextConductionInd="true">
                        <section classCode="DOCSECT">
                            <templateId root="1.2.276.0.76.10.3055"/>
                            <code code="11301-9" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
                                  displayName="ED diagnosis"/>
                            <title>Abschlussdiagnosen</title>
                            <text>
                                <list>
                                    <item ID="diag-1">
                                        <xsl:value-of select="diagnose_txt"/>
                                    </item>
                                </list>

                            </text>
                            <entry typeCode="COMP">
                                <act classCode="ACT" moodCode="EVN">
                                    <templateId root="1.2.276.0.76.10.4048"/>
                                    <id root="1.2.276.0.76.4.17.9814184919"
                                        extension="4193be05-5a9a-4e94-ad03-e35c0c5ca739"/>
                                    <code code="CONC" codeSystem="2.16.840.1.113883.5.6" displayName="Concern"/>
                                    <statusCode code="active"/>
                                    <effectiveTime>
                                        <low value="20150117"/>
                                    </effectiveTime>
                                    <entryRelationship typeCode="SUBJ">
                                        <observation classCode="OBS" moodCode="EVN">
                                            <templateId root="1.2.276.0.76.10.4049"/>
                                            <id root="1.2.276.0.76.4.17.9814184919"
                                                extension="45F99818-637B-4BE7-BC22-A7041C1CF813"/>
                                            <code code="29308-4" codeSystem="2.16.840.1.113883.6.1"
                                                  displayName="Diagnosis"/>
                                            <text>
                                                <reference value="#diag-1"/>
                                            </text>
                                            <statusCode code="completed"/>
                                            <effectiveTime>
                                                <low value="20150117"/>
                                            </effectiveTime>
                                            <value xsi:type="CD" code="S93.6" codeSystem="1.2.276.0.76.5.424"
                                                   codeSystemName="icd10gm2015"
                                                   displayName="Verstauchung und Zerrung sonstiger und nicht näher bezeichneter Teile des Fußes">
                                                <xsl:attribute name="code">
                                                    <xsl:value-of select="diagnose_code"/>
                                                </xsl:attribute>
                                                <originalText>
                                                    <xsl:value-of select="diagnose_name"/>
                                                </originalText>
                                            </value>
                                        </observation>
                                    </entryRelationship>
                                </act>
                            </entry>
                        </section>
                    </component>
                </structuredBody>
            </component>
        </ClinicalDocument>
    </xsl:template>
</xsl:stylesheet>