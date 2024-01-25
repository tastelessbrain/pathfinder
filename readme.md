# Pathfinder

## SAE Projectarbeit

Für die SAE-Projektarbeit habe ich einen Demobranch des Bots erstellt. Da Sie ihn selbst nicht starten können, da Ihnen der Zugang zum Azubicluster meines Ausbildungsbetriebs fehlt, finden Sie unten ein Video, welches demonstriert, dass der Bot funktioniert. Den vollständigen Sourcecode finden Sie auf GitHub (abgesehen von den API-Keys in der .env-Datei), die `pathfinder.py`, welche meine Abgabe darstellt, auch im Moodle. Das beigefügte Struktogramm stellt den Abschnitt "Main Script" in der `pathfinder.py` dar.

### Kommentar zur Nutzung von AI

Ich habe die `pathfinder.py` vollständig selbst geschrieben und AI nur zur Erklärung/Erschließung neuer Themengebiete genutzt. Ich verstehe den Code und kann Ihnen jeden Part erklären.

Bei den anderen Teilen des Bots, gerade bei der `momo.py`, welche ermöglicht, dass der Bot Antworten empfängt, habe ich verstärkt auf die Dokumentationsbeispiele und AI zurückgegriffen. An der `momo.py` habe ich, so gesehen, kein Urheberrecht. Die `columba.py`, welche den Mailversand übernimmt, stammt bis auf leichte Anpassungen aus Dokumentationsbeispielen. Meine Projektabgabe, die meine Eigenleistung enthält, würde ich aus Fairnessgründen also auf die `pathfinder.py` und die `wrapper.py` beschränken. Letztere übernimmt jedoch nur den regelmäßigen Start an bestimmten Tagen und die Überprüfung, ob Feiertag oder Wochenende ist. Sie ist also für den Sinn des Projekts vernachlässigbar.

### Funktion/Arbeitsweise

Das Hauptskript ruft, wenn es gestartet wird und die Konfiguration bereits vorliegt, die Webseite auf, auf der die Wohnungen eingestellt werden. Der HTML-Code wird nach Wohnungen gefiltert. Diese werden zunächst noch im XML-Format extrahiert. Dann wird für jede Wohnung eine Instanz der Klasse Wohnung erzeugt, und diese werden wiederum als ein Dictionary-Array im JSON-Format abgespeichert. Nun werden aus den jeweiligen Detail-Posts zu den Wohnungen noch fehlende Infos nachgetragen. Als nächstes wird verglichen, ob die gefundenen Wohnungen mir schon bekannt sind oder nicht. Sind mir die Wohnungen noch unbekannt, wurden erneut online gestellt und erfüllen die in der Konfiguration festgelegten Kriterien wie Kaltmiete und Wohnfläche, werden die Daten in ein Nachrichtentemplate eingefügt und mir über Telegram zugeschickt. Tritt während der Verarbeitung der HTML-Requests ein Fehler auf, werde ich ebenfalls benachrichtigt, und der Fehler wird geloggt. Die gefundenen Wohnungen werden in der `saved_search_results.json` gespeichert. Sensible Informationen wie API-Keys oder Chat-IDs werden in der `.env`-Datei gespeichert und mit der Python-Funktion `load_dotenv()` erst zur Laufzeit geladen und dann wieder verworfen. Im letzten Durchlauf eines Tages wird eine Abschlussnachricht an den User geschickt, der ihn über den tagesaktuellen Status der Suche informiert. Im erwähnten Demo-Modus ruft der Bot nicht die Original-Seite auf, sondern eine "cached Version", die bei mir lokal läuft. Die Daten der Seite habe ich so manipuliert, dass 2 Wohnungen "vorhanden" sind. Nur eine erfüllt die Kriterien, um zu demonstrieren, dass die Anwendung der Konfiguration funktioniert. Da sich dieses Feature aber noch in der Entwicklung befindet, habe ich es so implementiert, dass auch die Wohnungen, die nicht die Kriterien erfüllen, in den Suchergebnissen gespeichert werden und im `result_counter` gezählt werden, damit ich ggf. manuell nachschauen kann.

#### Hinweis zur Lesbarkeit der Kommentare

Sie fragen sich vermutlich, warum ich sowohl `#`, `#!`, als auch `#TODO` verwende. Dies ist einem VS Code Plugin geschuldet, welches mir verschiedenfarbige Kommentarkategorien erlaubt.
