-- PROJEKTY
INSERT INTO projects (id, title, description, owner_id, created_at) VALUES 
(1, 'Biurowiec Złota', 'Generalne wykonawstwo, stan surowy otwarty.', 1, '2026-02-26 08:00:00'),
(2, 'Hala Logis', 'Budowa centrum logistycznego 50 000 m2.', 1, '2026-02-26 08:05:00'),
(3, 'Osiedle Dębowe', 'Kompleks 5 budynków wielorodzinnych z garażami podziemnymi.', 1, '2026-02-26 08:10:00'),
(4, 'Modernizacja Mostu Północnego', 'Wzmocnienie konstrukcji stalowej i wymiana nawierzchni.', 1, '2026-02-26 08:15:00');

-- DOKUMENTY
INSERT INTO documents (id, file_name, storage_key, content_type, size, content_hash, owner_id, project_id, created_at) VALUES 
(1, 'dziennik_budowy_tom1.pdf', 'mock/dziennik1.pdf', 'application/pdf', 5242880, 'hash1', 1, 1, '2026-02-26 08:20:00'),
(2, 'projekt_wykonawczy_architektura.pdf', 'mock/architektura.pdf', 'application/pdf', 15242880, 'hash2', 1, 1, '2026-02-26 08:22:00'),
(3, 'specyfikacja_ppoz_hala.pdf', 'mock/ppoz.pdf', 'application/pdf', 2048000, 'hash3', 1, 2, '2026-02-26 08:25:00'),
(4, 'raport_geotechniczny.pdf', 'mock/geo.pdf', 'application/pdf', 8048000, 'hash4', 1, 3, '2026-02-26 08:30:00'),
(5, 'dziennik_budowy_osiedle.pdf', 'mock/dziennik2.pdf', 'application/pdf', 3145728, 'hash5', 1, 3, '2026-02-26 08:31:00'),
(6, 'ekspertyza_mostu_2025.pdf', 'mock/most.pdf', 'application/pdf', 12145728, 'hash6', 1, 4, '2026-02-26 08:35:00');

-- BIBLIOTEKI SZABLONÓW
INSERT INTO template_libraries (id, name, industry, description, is_global, creator_id) VALUES 
(1, 'Standardy BHP', 'BHP', 'Szablony kontroli, audytów i raportów powypadkowych na budowie.', 1, 1),
(2, 'Odbiory Instalacji', 'Budownictwo', 'Protokoły elektryczne, sanitarne i HVAC.', 1, 1),
(3, 'Zarządzanie Projektem', 'Zarządzanie', 'Tygodniowe i miesięczne raporty postępu prac dla inwestora.', 1, 1);

-- SZABLONY
INSERT INTO templates (id, name, description, owner_id, created_at) VALUES 
(1, 'Tygodniowy Raport BHP', 'Cotygodniowy raport z obchodu placu budowy pod kątem bezpieczeństwa.', 1, '2026-02-26 08:40:00'),
(2, 'Protokół Odbioru Zbrojenia', 'Weryfikacja zbrojenia przed rozpoczęciem betonowania.', 1, '2026-02-26 08:45:00'),
(3, 'Raport Postępu Prac (Miesięczny)', 'Zbiorcze zestawienie wykonanych prac dla inwestora i Inspektora Nadzoru.', 1, '2026-02-26 08:50:00'),
(4, 'Inspekcja PPOŻ', 'Weryfikacja zabezpieczeń przeciwpożarowych na obiekcie.', 1, '2026-02-26 08:55:00');

-- PRZYPISANIE SZABLONÓW DO BIBLIOTEK
INSERT INTO template_library_link (template_id, library_id) VALUES 
(1, 1),
(2, 2),
(3, 3),
(4, 1),
(4, 2);

-- WĘZŁY SZABLONÓW (Template Nodes)
INSERT INTO template_nodes (id, template_id, parent_id, type, data, created_at) VALUES 
('node-1', 1, NULL, 'section', '{"title": "1. Identyfikacja Zagrożeń", "show_title": true, "heading_level": 1, "page_before_break": false}', '2026-02-26 09:00:00'),
('node-2', 1, 'node-1', 'rag_extraction', '{"prompt": "Wypisz wszystkie incydenty BHP z dziennika budowy z ostatnich 7 dni.", "fallback_text": "Brak zarejestrowanych incydentów w danym okresie."}', '2026-02-26 09:01:00'),
('node-3', 1, NULL, 'section', '{"title": "2. Szkolenia załogi", "show_title": true, "heading_level": 1, "page_before_break": false}', '2026-02-26 09:02:00'),
('node-4', 1, 'node-3', 'static_text', '{"text": "Wszyscy pracownicy przebywający na placu budowy odbyli obowiązkowe instruktaże stanowiskowe."}', '2026-02-26 09:03:00'),

('node-5', 2, NULL, 'section', '{"title": "1. Zgodność z projektem", "show_title": true, "heading_level": 1, "page_before_break": false}', '2026-02-26 09:10:00'),
('node-6', 2, 'node-5', 'rag_extraction', '{"prompt": "Czy w dzienniku budowy odnotowano jakiekolwiek odstępstwa od projektu konstrukcyjnego w zakresie zbrojenia stropu?", "fallback_text": "Zbrojenie wykonano zgodnie z projektem."}', '2026-02-26 09:11:00'),

('node-7', 3, NULL, 'section', '{"title": "1. Status robót żelbetowych", "show_title": true, "heading_level": 1, "page_before_break": false}', '2026-02-26 09:20:00'),
('node-8', 3, 'node-7', 'rag_extraction', '{"prompt": "Wypunktuj wszystkie wylane w tym miesiącu elementy konstrukcyjne wraz z ich kubaturą na podstawie wpisów w dzienniku.", "fallback_text": "Brak danych o betonowaniu w tym miesiącu."}', '2026-02-26 09:21:00');

-- CZATY RAG
INSERT INTO chats (id, title, project_id, user_id, created_at) VALUES 
(1, 'Opóźnienia w betonowaniu', 1, 1, '2026-02-26 09:30:00'),
(2, 'Wymagania pożarowe dachu', 2, 1, '2026-02-26 09:45:00'),
(3, 'Warunki gruntowe pod garaż', 3, 1, '2026-02-26 10:00:00');

-- WIADOMOŚCI CZATU
INSERT INTO messages (id, chat_id, role, content, created_at) VALUES 
(1, 1, 'user', 'Dlaczego wstrzymano betonowanie stropu nad parterem w zeszłym tygodniu?', '2026-02-26 09:31:00'),
(2, 1, 'assistant', 'Zgodnie z dziennikiem budowy (tom 1, strona 14), powodem były intensywne opady deszczu oraz brak zgody Inspektora Nadzoru na ułożenie mieszanki betonowej w zalanych szalunkach.', '2026-02-26 09:31:10'),
(3, 1, 'user', 'Ile dni trwał przestój?', '2026-02-26 09:32:00'),
(4, 1, 'assistant', 'Przestój trwał 3 dni robocze (od 12 do 14 maja włącznie). Wznowienie prac odnotowano 15 maja po wypompowaniu wody.', '2026-02-26 09:32:15'),

(5, 2, 'user', 'Jaką odporność ogniową musi mieć stal dachu na tej hali?', '2026-02-26 09:46:00'),
(6, 2, 'assistant', 'Zgodnie z dokumentem "specyfikacja_ppoz_hala.pdf" (sekcja 4.2), główna konstrukcja stalowa dachu musi spełniać kryterium R15. Słupy nośne muszą posiadać odporność R30.', '2026-02-26 09:46:12'),
(7, 2, 'user', 'Czy narzucono sposób zabezpieczenia tej stali?', '2026-02-26 09:47:00'),
(8, 2, 'assistant', 'Tak. Specyfikacja (punkt 4.3) wprost wskazuje na konieczność zabezpieczenia słupów nośnych za pomocą systemu powłok pęczniejących (farb ogniochronnych).', '2026-02-26 09:47:10'),

(9, 3, 'user', 'Na jakiej głębokości znajduje się woda gruntowa na osiedlu?', '2026-02-26 10:01:00'),
(10, 3, 'assistant', 'Raport geotechniczny (strona 8, tabela 2) wskazuje, że swobodne zwierciadło wody gruntowej stabilizuje się na rzędnej 3.20 m p.p.t (pod poziomem terenu).', '2026-02-26 10:01:15');