import streamlit as st
from urllib.error import URLError
import pandas as pd
from utilities import utils
import os

def clear_summary():
    st.session_state['summary'] = ""

def get_custom_prompt():
    customtext = st.session_state['customtext']
    customprompt = "{}".format(customtext)
    return customprompt

def customcompletion():
    _, response = utils.get_completion(get_custom_prompt(), max_tokens=st.tokens_response, model=os.getenv('OPENAI_ENGINES', 'text-davinci-003'), temperature=st.temperature)
    st.session_state['result'] = response['choices'][0]['text'].encode().decode()
    st.session_state['response'] = response['usage']

prompts = {
    "None": "",
    
    "IDOS (CZ)": '''
    Potřebuju se dostat na Budějovickou z Karlova náměstí dneska, abych byl na místě do 16:00.

    Z požadavku výše na dopravní informace a navigaci, extrahuj následující:

    1. Odkud se pojede
    2. Kam se pojede
    3. Který den je plánovaný odjezd, když není napiš "není"
    4. Který čas je plánovaný odjezd, když není napiš "není"
    5. Který den je plánovaný příjezd, když není napiš "není"
    6. Který čas je plánovaný příjezd, když není napiš "není"
    7. Může být spoj s přestupem? Když není uvedeno, napiš "není"

    Výstup v JSON v Markdown formátu.

    ''',

    "Medical (CZ)": '''
    Lékař: Dobrý den,paní Novotná.Vy jste u nás ještě nebyla, že? Pacientka: Ne, pane doktore, jsem tu poprvé. 
    Lékař: Jsem doktor Novák, těší mě. Posaďte se tady do křesla, prosím. 
    Pacientka: Děkuji, pane doktore. Posílá mě za vámi moje praktická lékařka. V poslední době mám potíže se soustředěním a pamětí vůbec. 
    Lékař: Ano, přečetl jsem si její zprávu. Taky jsem si prošel dotazník, který jste vyplnila na recepci se sestřičkou.
    Teď bych se ale rád na některé věci zeptal ještě jednou. Souhlasíte? 
    Pacientka: Samozřejmě, pane doktore, klidně se ptejte.
    Lékař: Nejdřív je pro kontrolu. Jake je vaše rodné číslo?
    Pacientka: 7232329872
    Lékař: děkuji.

    Z konverzace výše, extrahuj následující:

    1. Jaká jsou jména dotyčných v textu? (klíč: names)
    2. Rodné číslo pacientky? (klíč: rc)
    3. Kdo posílá pacienta k lékař? (klíč: source)
    4. Co pacienta trápí? (klíč: reason)

    Výstup v JSON v Markdown formátu. 

    ''',

    "Banking 1 (CZ)": '''
    Extrahuj následující informace z telefonní komunikace níže:

    1. Důvod hovoru (klíč: reason)
    2. Jména účastníků hovoru jako pole (klíč: names)
    3. Krátké shrnutí hovoru (klíč: summary)

    Prosím o odpověď v JSON formát s použitím klíču výše.
    Formátuj výstup jako JSON object nazvaný "results" a výstup udělej v Markdown.

    Telefonní komunikace:

    Dobrý den, pane Štěpánek. Jsem z banky a potřebuji se s vámi poradit ohledně vašeho účtu.
    Máte nějaké dotazy?
    Štěpánek: Ano, pane bankéři. Mám dotaz ohledně výše úvěru.
    Bankéř: Ano, pane Štěpánek. Jaký úvěr máte na mysli?
    Štěpánek: Já bych chtěl zvýšit úvěr na bydlení.
    Bankéř: Ano, pane Štěpánek. Jakou máte v současné době výši úvěru?
    Štěpánek: Mám úvěr na bydlení v hodnotě 1 000 000 Kč.
    Bankéř: Ano, pane Štěpánek. Jakou výši byste chtěl zvýšit?
    Štěpánek: Chtěl bych zvýšit úvěr na bydlení na 1 500 000 Kč.
    ''',

    "Banking 2 (CZ)": '''
    Extrahuj následující informace z telefonní komunikace níže:

    1. Důvod hovoru (klíč: reason)
    2. Jména účastníků hovoru jako pole (klíč: names)
    3. Byla zmíněna konrétní pojišťovna, jestli ano jaká (klíč: insurrance_company)
    4. Krátké shrnutí hovoru (klíč: summary)

    Prosím o odpověď v JSON formát s použitím klíču výše.
    Formátuj výstup jako JSON object nazvaný "results" a výstup udělej v Markdown.

    Telefonní komunikace:

    Bankéř: Dobrý den, u telefonu Alena Nováková. z České spořitelny, hovořím, prosím, s paní Dagmar Novotnou?
    Klient: No,jo. 
    Bankéř: Paní Novotná, vzhledem k tomu, že si vážíme toho, že jste naší klientkou, máte nyní nárok na 
    speciální doplňkové služby k vašemu účtu. Máte na mě chvilku čas?
    Klient: No, ani moc ne.
    Bankéř: A můžu vás kontaktovat později?
    Klient: No, hmm, a vo co teda de? Tak teda povidejte. 
    Bankéř: Vy u vašeho účtu máte i platební kartu, používáte ji často?
    Klient: Vobčas s ní zaplatím v obchodě. 
    Bankéř: A víte o tom, že ta karta není pojišťená? My teď totiž nabízíme za zvýhodněnou cenu 
    pojištění é-é pro případ stráty nebo krádeže vaší platební karty. To znamená, že gdyby 
    došlo k té nepříjemnosti, že vám karta nebo osobní věci é-é budou odcizeny, tak to máte 
    zajištěné. 
    Klient: No, to je dobrý. Sme v létě byli na dovolené a voni mi tam ukradli kabelku i se všema 
    věcma a penězama. 
    Bankéř: Ano, no a to pojištění vám kryje třeba neoprávněný výběr z účtu i s použitim pinu a před 
    nahlášením, peníze, které byste vybrala v hotovosti a někdo vás okradl é-é, ale taky i ty 
    osobní věci é-é jako třeba mobilní telefon nebo to co by z něj bylo provoláno a taky 
    veškeré poplatky a náklady spojené se situací é-é, jako třeba výroba nových klíčů od 
    auta, výměna zámků, poplatky za nové doklady, apod. Jsou to drahé záležitosti a tohle je 
    tím pojištěním karty všechno hrazeno. 
    Klient: A kolik si za to teda účtujou?
    Bankéř: Je to pouze za jednorázový roční poplatek 170 koruNovotná
    Klient: A to musim na pobočku?
    Bankéř: Ne, paní Novotná, pokud chcete, můžeme Vám to pojištění karty é-é nastavit společně, bude 
    platné do dvou pracovních dnů.
    Klient: Tak jo, tak mi to tam teda nastavte.
    Bankéř: Zeptám se tedy jenom, souhlasíte s tím, abych vám pojištění karty a osobních věcí 
    nastavila?
    Klient: Ano.
    Bankéř: A souhlasíte s předáním údajů pojistiteli, což je pojišťovna Kooperativa?
    Klient: Ano.
    Bankéř: A ještě se zeptám, jestli souhlasíte s jednorázovým ročním poplatkem 170 korun?
    Klient: Ano.
    Bankéř: Já vám děkuji, pojištění je nastaveno. A můžu se ještě zeptat?
    Klient: Ne, už ne. Už stačilo.
    Bankéř: V tom případě Vás tedy nebudu zdržovat a popřeji hezký den.
    Klient: Na schledanou.
    Bankéř: Na slyšenou. 
    ''',

    "Noviny (CZ)": '''
    Extract information from the news article below. In detail, please perform

    1. one sentence summary in Czech
    2. All names in article and their roles
    3. Article source

    Return the results in a formatted JSON document using markdown with the keys summary, names, and source.

    News article:
    Česká pošta je tradičně připravená nabídnout veřejnosti nové poštovní známky s portrétem čerstvě zvoleného prezidenta Petra Pavla. Vznik prezidentských známek, ale i jejich případná podoba, ovšem závisí na rozhodnutí nově zvolené hlavy státu. Mluvčí České pošty Matyáš Vitík připomněl, že se jedná o tradici, nikoliv o právní povinnost.
    Podle Vitíka známka nevznikne, pokud ji Pavel nebude chtít. „Budeme plně respektovat přání pana prezidenta,“ dodal.
    Vznik nové prezidentské známky je tak prozatím nejistý. Pavel totiž již v minulosti prohlásil, že známky se svou podobiznou nechce. V rozhovoru pro iROZHLAS neprodleně po vítězství v prezidentské volbě dodal, že se mu na známkách mnohem víc líbí motivy českých hradů a zámků, popřípadě přírodních krás.
    Zdroj: https://www.idnes.cz/

    ''',

    "Generovaní komunikace (CZ)": '''
    Okno údržby je naplánováno na 14. února od 14:00 do 15:00, linka bude funkční, ale očekávají se odstávky.

    Napište formální mail zákaznikům

    - Nabídněte pomoc v rámci info@operations.cz, ne telefonicky
    - Požádejte o prominutí
    - udělejte vtip o IT

    Mail:
    ''',

    "Python (EN)": ''' 
    Can you explain Python object model? Please use few examples and markdown to format your answer.
    ''',

    "Content generation - Agenda (EN)": '''
    Write agenda for AI Bootcamp. Use time format from-to. Create teaser summary for each agenda item. Leave some time for welcome and after event for networking. Put a snack before the hands-on lab and make it part of agenda. Start at 1PM. Time format 00:00.

    - welcome, 15min
    - introduction Azure AI Services, 50min
    - Azure OpenAI, 50min
    - snack
    - Hands-on lab, 120min
    - networking

    Agenda:
    ''',

    "SQL (EN)": '''
    Schema for table: organizations
        uuid Text
            name Text
            roles Text
            country_code Text
            region Text
            city Text
            status Text
            short_description Text
            category_list Text
            num_funding_rounds Float
            total_funding_usd Float
            founded_on Date
            employee_count Text
            email Text
            primary_role Text
            
        Data for table: organizations:
                                        uuid                        name    roles  \
        0  ac323097-bdd0-4507-9cbc-6186e61c47a5       Bootstrap Enterprises  company   
        1  717ce629-38b6-494d-9ebf-f0eeb51506f8                  Campanizer  company   
        2  c8cbaa69-c9db-44e2-9ffa-eb4722a62fe3                       Cambr  company   
        3  5ab1ae3d-c3a1-4268-a532-b500d3dd6182                  CallMeHelp  company   
        4  143f840b-551c-4dbd-a92b-0804d654b5cf  California Cannabis Market  company   

        country_code      region           city     status  \
        0         <NA>        <NA>           <NA>  operating   
        1          USA    Colorado        Boulder  operating   
        2          USA    New York       New York  operating   
        3          GBR   Stockport      Stockport  operating   
        4          USA  California  San Francisco     closed   

                                        short_description  \
        0  Bootstrap Enterprises is an organic waste mana...   
        1  Campanizer organizes schedule and coordinates ...   
        2  Cambr enables companies to build and scale fin...   
        3  CallMeHelp provides early warning and care ove...   
        4  California Cannabis Market is an information t...   

                                            category_list  num_funding_rounds  \
        0              Consulting,Organic,Waste Management                 NaN   
        1                Information Technology,Scheduling                 NaN   
        2                       Banking,Financial Services                 NaN   
        3                     Fitness,Health Care,Wellness                 NaN   
        4  B2B,Information Services,Information Technology                 NaN   

        total_funding_usd founded_on employee_count                 email  \
        0                NaN        NaT        unknown                  <NA>   
        1                NaN 2017-01-01           1-10  hello@campanizer.com   
        2                NaN        NaT        unknown       sales@cambr.com   
        3                NaN 2017-01-01           1-10                  <NA>   
        4                NaN 2018-01-01           1-10                  <NA>   

        primary_role  
        0      company  
        1      company  
        2      company  
        3      company  
        4      company  
            

        Schema for table: investments
        uuid Text
            name Text
            funding_round_uuid Text
            funding_round_name Text
            investor_uuid Text
            investor_name Text
            investor_type Text
            is_lead_investor Boolean
            
        Data for table: investments:
                                        uuid  \
        0  524986f0-3049-54a4-fa72-f60897a5e61d   
        1  6556ab92-6465-25aa-1ffc-7f8b4b09a476   
        2  0216e06a-61f8-9cf1-19ba-20811229c53e   
        3  dadd7d86-520d-5e35-3033-fc1d8792ab91   
        4  581c4b38-9653-7117-9bd4-7ffe5c7eba69   

                                                        name  \
        0                Accel investment in Series A - Meta   
        1             Greylock investment in Series B - Meta   
        2  Meritech Capital Partners investment in Series...   
        3  Trinity Ventures investment in Series B - Phot...   
        4        Founders Fund investment in Series A - Geni   

                            funding_round_uuid      funding_round_name  \
        0  d950d7a5-79ff-fb93-ca87-13386b0e2feb         Series A - Meta   
        1  6fae3958-a001-27c0-fb7e-666266aedd78         Series B - Meta   
        2  6fae3958-a001-27c0-fb7e-666266aedd78         Series B - Meta   
        3  bcd5a63d-ed99-6963-0dd2-e36f6582f846  Series B - Photobucket   
        4  60e6afd9-1215-465a-dd17-0ed600d4e29b         Series A - Geni   

                                investor_uuid              investor_name  \
        0  b08efc27-da40-505a-6f9d-c9e14247bf36                      Accel   
        1  e2006571-6b7a-e477-002a-f7014f48a7e3                   Greylock   
        2  8d5c7e48-82da-3025-dd46-346a31bab86f  Meritech Capital Partners   
        3  7ca12f7a-2f8e-48b4-a8d1-1a33a0e275b9           Trinity Ventures   
        4  fb2f8884-ec07-895a-48d7-d9a9d4d7175c              Founders Fund   

        investor_type  is_lead_investor  
        0  organization              True  
        1  organization              True  
        2  organization              True  
        3  organization              <NA>  
        4  organization              True  
            

        Schema for table: funding_rounds
        uuid Text
            region Text
            city Text
            investment_type Text
            announced_on Date
            raised_amount_usd Float
            post_money_valuation_usd Float
            investor_count Float
            org_uuid Text
            org_name Text
            lead_investor_uuids Text
            
        Data for table: funding_rounds:
                                        uuid      region            city  \
        0  8a945939-18e0-cc9d-27b9-bf33817b2818  California      Menlo Park   
        1  d950d7a5-79ff-fb93-ca87-13386b0e2feb  California      Menlo Park   
        2  6fae3958-a001-27c0-fb7e-666266aedd78  California      Menlo Park   
        3  bcd5a63d-ed99-6963-0dd2-e36f6582f846    Colorado          Denver   
        4  60e6afd9-1215-465a-dd17-0ed600d4e29b  California  West Hollywood   

        investment_type announced_on  raised_amount_usd  post_money_valuation_usd  \
        0           angel   2004-09-01           500000.0                       NaN   
        1        series_a   2005-05-01         12700000.0                98000000.0   
        2        series_b   2006-04-01         27500000.0               502500000.0   
        3        series_b   2006-05-01         10500000.0                       NaN   
        4        series_a   2007-01-17                NaN                10000000.0   

        investor_count                              org_uuid     org_name  \
        0             4.0  df662812-7f97-0b43-9d3e-12f64f504fbb         Meta   
        1             4.0  df662812-7f97-0b43-9d3e-12f64f504fbb         Meta   
        2             5.0  df662812-7f97-0b43-9d3e-12f64f504fbb         Meta   
        3             2.0  f53cb4de-236e-0b1b-dee8-7104a8b018f9  Photobucket   
        4             1.0  4111dc8b-c0df-2d24-ed33-30cd137b3098         Geni   

                                        lead_investor_uuids  
        0               3f47be49-2e32-8118-01a0-31685a4d0fd7  
        1               b08efc27-da40-505a-6f9d-c9e14247bf36  
        2  e2006571-6b7a-e477-002a-f7014f48a7e3,8d5c7e48-...  
        3                                               <NA>  
        4               fb2f8884-ec07-895a-48d7-d9a9d4d7175c  
            

        As a senior analyst, given the above schemas and data, write a detailed and correct Postgres sql query to answer the analytical question:

        "Who were the largest biotech investors in 2022?"

        Comment the query with your logic.

    ''',

    "QnA (EN)": '''
    Using the following text, answer the following question. If the answer is not contained within the text, say "I don't know."

    Text:
    """
    Oklo Mine (sometimes Oklo Reactor or Oklo Mines), located in Oklo, Gabon on the west coast of Central Africa, is believed to be the only natural nuclear fission reactor. Oklo consists of 16 sites at which self-sustaining nuclear fission reactions are thought to have taken place approximately 1.7 billion years ago, and ran for hundreds of thousands of years. It is estimated to have averaged under 100 kW of thermal power during that time.
    """

    Question: How many natural fission reactors have ever been discovered?

    Answer:
    ''',

    "Entity extraction": '''
    From the text below, extract the following entities in the following format:
    Companies: <comma-separated list of companies mentioned>
    People & titles: <comma-separated list of people mentioned (with their titles or roles appended in parentheses)>

    Text:
    """
    In March 1981, United States v. AT&T came to trial under Assistant Attorney General William Baxter. AT&T chairman Charles L. Brown thought the company would be gutted. He realized that AT&T would lose and, in December 1981, resumed negotiations with the Justice Department. Reaching an agreement less than a month later, Brown agreed to divestiture—the best and only realistic alternative. AT&T's decision allowed it to retain its research and manufacturing arms. The decree, titled the Modification of Final Judgment, was an adjustment of the Consent Decree of 14 January 1956. Judge Harold H. Greene was given the authority over the modified decree....

    In 1982, the U.S. government announced that AT&T would cease to exist as a monopolistic entity. On 1 January 1984, it was split into seven smaller regional companies, Bell South, Bell Atlantic, NYNEX, American Information Technologies, Southwestern Bell, US West, and Pacific Telesis, to handle regional phone services in the U.S. AT&T retains control of its long distance services, but was no longer protected from competition.
    """
    ''',

    "Information extraction": '''
    You must extract the following information from the phone conversation below:

    1. Call reason (key: reason)
    2. Cause of the incident (key: cause)
    3. Names of all drivers as an array (key: driver_names)
    4. Insurance number (key: insurance_number)
    5. Accident location (key: location)
    6. Car damages as an array (key: damages)
    7. A short, yet detailed summary (key: summary)

    Make sure fields 1 to 6 are answered very short, e.g. for location just say the location name
    Please answer in JSON using Markdown format, using the keys from above.

    Phone conversation:
    Hi I just had a car accident and wanted to report it. OK, I hope you're alright, what happened? I was driving on the I-18 and I hit another car. Are you OK? Yeah, I'm just a little shaken up. That's understandable. Can you give me your full name? Sure, it's Sarah standl. Do you know what caused the accident? I think I might have hit a pothole. OK, where did the accident take place? On the I-18 freeway. Was anyone else injured? I don't think so. But I'm not sure. OK, well we'll need to do an investigation. Can you give me the other drivers information? Sure, his name is John Radley. And your insurance number. OK. Give me a minute. OK, it's 546452. OK, what type of damages has the car? Headlights are broken and the airbags went off. Are you going to be able to drive it? I don't know. I'm going to have to have it towed. Well, we'll need to get it inspected. I'll go ahead and start the claim and we'll get everything sorted out. Thank you.

    JSON:
  
    ''',

    "Hallucination (bad)": '''
    If a vehicle will be used at any time, proof of automobile liability insurance is required with the following limits of coverage: $500,000 limit minimum combined single limit.

    Are the children insured?
    ''',

    "Hallucination (good)": '''
    If a vehicle will be used at any time, proof of automobile liability insurance is required with the following limits of coverage: $500,000 limit minimum combined single limit.

    Are the children insured? If the answer is not in the text, write "Answer not found".
    ''',

    "More precise answer (bad)": '''
    What is the annual energy demand in kWh for a single-family household with four people. Assume they are home 330 days per year.
    ''',

    "More precise answer (good)": '''
    What is the annual energy demand in kWh for a single-family household with four people. Assume they are home 330 days per year.
    
    Please think step by step and explain the calculation step by step.
    ''',

    "Remove PII (EN)": '''
    Read the following sales email. Remove any personally identifiable information (PII),
    and replace it with the appropriate placeholder. For example, replace the name "John Doe"
    with "[NAME]".

    Hi John,

    I'm writing to you because I noticed you recently purchased a new car. I'm a salesperson
    at a local dealership (Cheap Dealz), and I wanted to let you know that we have a great deal on a new
    car. If you're interested, please let me know.

    Thanks,

    Jimmy Smith

    Phone: 410-805-2345
    Email: jimmysmith@cheapdealz.com
    ''',
    


}

try:
    # Set page layout to wide screen and menu item
    menu_items = {
    'Get help': None,
    'Report a bug': None,
    'About': '''
     ## Embeddings App
     Embedding testing application.
    '''
    }
    st.set_page_config(layout="wide", menu_items=menu_items)

    if 'example' not in st.session_state:
        st.session_state['example'] = ""

    st.markdown("## Bring your own prompt")

    st.tokens_response = st.slider("Tokens response length", 100, 1000, 400)
    st.temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    # st.selectbox("Language", [None] + list(available_languages.keys()), key='translation_language')
    
    # parse dictionary of prompts yielding a list keys only
    example = st.selectbox(
                label="Examples",
                options=list(list(prompts.keys()))
            )

    # displaying a box for a custom prompt
    st.session_state['customtext'] = st.text_area(label="Prompt", key='prompt', height=400, value=prompts[example])
    st.button(label="Generate", on_click=customcompletion)
    
    # displaying the summary
    st.markdown("**Generated response**")
    
    result = ""
    if 'result' in st.session_state:
        result = st.session_state['result']
    # st.text_area(label="OpenAI result", value=result, height=200)
    
    response = "None"
    if 'response' in st.session_state:
        response = st.session_state["response"]
        st.write(result)
        st.write("Response details:")
        st.write(response)

except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )