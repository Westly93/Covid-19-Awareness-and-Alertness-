import os
from datetime import datetime
from kivy.factory import Factory as f
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.tab import MDTabsBase
from kivymd.app import MDApp
from kivy.core.window import Window
#from covid_helpers import toolbar_helper
from kivymd.uix.list import TwoLineListItem, MDList, OneLineListItem
from kivy.uix.scrollview import ScrollView
from kivymd.uix.label import MDLabel, MDIcon
from kivy.properties import StringProperty, ListProperty
from kivy.garden.matplotlib.backend_kivy import FigureCanvas
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivymd.uix.card import MDCard
# importing pandas for reading csv files
import matplotlib.pyplot as plt
import pandas as pd
from urllib import request
from bs4 import BeautifulSoup as bs
import requests

Window.size= (350, 670)

class OneLineListItemAligned(OneLineListItem):
    def __init__(self, halign, **kwargs):
        super(OneLineListItemAligned, self).__init__(**kwargs)
        self.ids._lbl_primary.halign = halign

class Tab(FloatLayout, MDTabsBase):
    pass

class ContentNavigationDrawer(BoxLayout):
    pass

class MyLabel(MDLabel):
    pass



class MainApp(MDApp):
    def build(self):
        self.vaccine_questions_and_answers()
        #self.display_image()
        self.create_plots()

    def on_start(self):
        self.theme_cls.primary_palette= "Cyan"
        self.theme_cls.primary_hue= "900"
        self.new_updates("https://covid19.who.int/WHO-COVID-19-global-table-data.csv")
        #self.get_precautions()

    def new_updates(self, url):
        try:
            request.urlopen(url, timeout= 5)
            df= pd.read_csv(url, index_col= 0)
            df.reset_index(inplace= True)
            df= df[df['Name']=="Zimbabwe"]
            df= df[['Cases - cumulative total', 'Deaths - cumulative total', 'Cases - newly reported in last 24 hours', 'Deaths - newly reported in last 24 hours']]
            df= df.rename(columns= {'Cases - cumulative total': 'Coronavirus Cases',
                                 'Deaths - cumulative total': 'Deaths',
                                 'Cases - newly reported in last 24 hours': 'New Cases',
                                 'Deaths - newly reported in last 24 hours': 'New Deaths'
                                 })
            list_view= MDList()
            scroll= ScrollView()
            list_view.add_widget(OneLineListItemAligned(text= f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", halign= 'center'))

            for item in df.columns:

                new_update= TwoLineListItem(text= item, secondary_text= str(df[item].values[0]))
                list_view.add_widget(new_update)
            respont= bs(requests.get('https://www.worldometers.info/coronavirus/country/zimbabwe/').content)
            recovery= respont.find_all('div', class_= 'maincounter-number')
            list_view.add_widget(TwoLineListItem(text= 'Recovered', secondary_text= str(recovery[-1].text)))

            scroll.add_widget(list_view)
            self.root.ids.corona.add_widget(scroll)

        except Exception as e:
            icon_label= MDIcon(icon= 'network-off', halign= 'center' ,pos_hint= {'center_x': 0.5, 'center_y': 0.7})
            label= MDLabel(text= 'You are not connected Please check your internet settings!!',
                halign= 'center', pos_hint= {'center_x': 0.5, 'center_y': 0.5})
            self.root.ids.corona.add_widget(icon_label)
            self.root.ids.corona.add_widget(label)


    def vaccine_questions_and_answers(self):
        try:


            soup= bs(requests.get('https://www.who.int/news-room/q-a-detail/coronavirus-disease-(covid-19)-vaccines').content)
            container= soup.find_all('div', class_= 'sf-accordion__panel')


            for item in container:

                questions=  item.find('a').text
                answers= item.find('div', class_= 'sf-accordion__content').text
                self.root.ids.box.add_widget(MyLabel(text= f'{questions.strip().upper()}{answers}'))


        except:
            self.root.ids.vaccine.add_widget(MDIcon(icon= 'network-off', halign= 'center' ,pos_hint= {'center_x': 0.5, 'center_y': 0.7}))
            self.root.ids.vaccine.add_widget(MyLabel(text= 'You are not connected Please check your internet settings!!',
                halign= 'center', pos_hint= {'center_x': 0.5, 'center_y': 0.5}))


    #def get_image_list(self, folder_name):
    #    image_list= []
    #    for image in os.listdir(folder_name):
    #        image_list.append(image)

    #    return image_list

    #def display_image(self):
    #    image_list= []
    #    for image in self.get_image_list('images'):
    #        image_list.append(image)


    #    for image in image_list:
    #        self.root.ids.cards.add_widget(f.MyTile(source= f'images/{image}'))
    #    return self


    def create_plots(self):
        try:
            # Loading data into the pandas dataframe
            data= pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv')
            data= data[data['location']== 'Zimbabwe']
            data['date']= pd.to_datetime(data['date'])

            result= data.groupby('date').sum()
            dates= [date for date in data['date'].unique()]
            plt.style.use('Solarize_Light2')


            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize= (4,8), sharex= False)

            ax1.plot(dates, result['new_cases'], linewidth= 1, label= 'confirmed cases', color= 'k')
            ax1.fill_between(dates, result['new_cases'], color= 'k')
            ax1.set_title('Daily New Cases')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Population')
            ax1.spines['top'].set_visible(False)
            ax1.spines['right'].set_visible(False)

            new_deaths= data['new_deaths'].values

            ax2.plot(dates, new_deaths, linewidth= 1, label= 'confirmed deaths', color= 'k')
            ax2.fill_between(dates, new_deaths, color= 'k')
            ax2.set_title('Daily Deaths')
            ax3.spines['right'].set_visible(False)

            ax2.set_xlabel('Date')
            ax2.set_ylabel('Population')
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)


            new_test= data['new_tests'].values

            ax3.plot(dates, new_test, linewidth= 1, color= 'k')
            ax3.fill_between(dates, new_test, color= 'k')
            ax3.set_title('Daily Tests')
            ax3.set_xlabel('Date')# creating lables for the x-axis
            ax3.set_ylabel('Population') # creating lables for the y-axis
            ax3.set_yscale('log') # presenting population figures in thousands
            # Remove the top and right borders from the plots
            ax3.spines['top'].set_visible(False)
            ax3.spines['right'].set_visible(False)

            #date formatting for the nice looking plots
            fig.autofmt_xdate()
            fig.tight_layout()

            # create some spaccing between the plots
            fig.subplots_adjust(wspace= 1, hspace= 1)


            #Loading the plots to the kivy window
            self.root.ids.plots.add_widget(FigureCanvasKivyAgg(fig))



        except:
            # This should run when there is no internet connection
            self.root.ids.load_failure.add_widget(MDIcon(icon= 'network-off', halign= 'center' ,pos_hint= {'center_x': 0.5, 'center_y': 0.7}))
            self.root.ids.load_failure.add_widget(MDLabel(text= 'You are not connected please check your internet settings!!', halign= 'center', pos_hint= {'center_x': 0.5, 'center_y': 0.5}))


    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        '''Called when switching tabs.

        :type instance_tabs: <kivymd.uix.tab.MDTabs object>;
        :param instance_tab: <__main__.Tab object>;
        :param instance_tab_label: <kivymd.uix.tab.MDTabsLabel object>;
        :param tab_text: text or name icon of tab;
        '''
        pass

if __name__== '__main__':
    MainApp().run()
