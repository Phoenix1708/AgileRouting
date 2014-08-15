# ./raw/weather.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:69f3f258abdddf27f8cb984cd940cf14ba4a42ab
# Generated 2014-07-09 15:49:24.202705 by PyXB version 1.2.3
# Namespace http://ws.cdyne.com/WeatherWS/

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import io
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:371fe626-0778-11e4-b50d-109add58a6cf')

# Version of PyXB used to generate the bindings
_PyXBVersion = '1.2.3'
# Generated bindings are not compatible across PyXB versions
if pyxb.__version__ != _PyXBVersion:
    raise pyxb.PyXBVersionError(_PyXBVersion)

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

# NOTE: All namespace declarations are reserved within the binding
Namespace = pyxb.namespace.NamespaceForURI(u'http://ws.cdyne.com/WeatherWS/', create_if_missing=True)
Namespace.configureCategories(['typeBinding', 'elementBinding'])

def CreateFromDocument (xml_text, default_namespace=None, location_base=None):
    """Parse the given XML and use the document element to create a
    Python instance.

    @param xml_text An XML document.  This should be data (Python 2
    str or Python 3 bytes), or a text (Python 2 unicode or Python 3
    str) in the L{pyxb._InputEncoding} encoding.

    @keyword default_namespace The L{pyxb.Namespace} instance to use as the
    default namespace where there is no default namespace in scope.
    If unspecified or C{None}, the namespace of the module containing
    this function will be used.

    @keyword location_base: An object to be recorded as the base of all
    L{pyxb.utilities.utility.Location} instances associated with events and
    objects handled by the parser.  You might pass the URI from which
    the document was obtained.
    """

    if pyxb.XMLStyle_saxer != pyxb._XMLStyle:
        dom = pyxb.utils.domutils.StringToDOM(xml_text)
        return CreateFromDOM(dom.documentElement)
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    saxer = pyxb.binding.saxer.make_parser(fallback_namespace=default_namespace, location_base=location_base)
    handler = saxer.getContentHandler()
    xmld = xml_text
    if isinstance(xmld, unicode):
        xmld = xmld.encode(pyxb._InputEncoding)
    saxer.parse(io.BytesIO(xmld))
    instance = handler.rootObject()
    return instance

def CreateFromDOM (node, default_namespace=None):
    """Create a Python instance from the given DOM node.
    The node tag must correspond to an element declaration in this module.

    @deprecated: Forcing use of DOM interface is unnecessary; use L{CreateFromDocument}."""
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    return pyxb.binding.basis.element.AnyCreateFromDOM(node, default_namespace)


# Complex type [anonymous] with content type EMPTY
class CTD_ANON (pyxb.binding.basis.complexTypeDefinition):
    """Complex type [anonymous] with content type EMPTY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 6, 8)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        
    })



# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_ (pyxb.binding.basis.complexTypeDefinition):
    """Complex type [anonymous] with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 9, 8)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://ws.cdyne.com/WeatherWS/}GetWeatherInformationResult uses Python identifier GetWeatherInformationResult
    __GetWeatherInformationResult = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'GetWeatherInformationResult'), 'GetWeatherInformationResult', '__httpws_cdyne_comWeatherWS_CTD_ANON__httpws_cdyne_comWeatherWSGetWeatherInformationResult', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 11, 12), )

    
    GetWeatherInformationResult = property(__GetWeatherInformationResult.value, __GetWeatherInformationResult.set, None, None)

    _ElementMap.update({
        __GetWeatherInformationResult.name() : __GetWeatherInformationResult
    })
    _AttributeMap.update({
        
    })



# Complex type {http://ws.cdyne.com/WeatherWS/}ArrayOfWeatherDescription with content type ELEMENT_ONLY
class ArrayOfWeatherDescription_ (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ws.cdyne.com/WeatherWS/}ArrayOfWeatherDescription with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ArrayOfWeatherDescription')
    _XSDLocation = pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 15, 6)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://ws.cdyne.com/WeatherWS/}WeatherDescription uses Python identifier WeatherDescription
    __WeatherDescription = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'WeatherDescription'), 'WeatherDescription', '__httpws_cdyne_comWeatherWS_ArrayOfWeatherDescription__httpws_cdyne_comWeatherWSWeatherDescription', True, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 17, 10), )

    
    WeatherDescription = property(__WeatherDescription.value, __WeatherDescription.set, None, None)

    _ElementMap.update({
        __WeatherDescription.name() : __WeatherDescription
    })
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ArrayOfWeatherDescription', ArrayOfWeatherDescription_)


# Complex type {http://ws.cdyne.com/WeatherWS/}WeatherDescription with content type ELEMENT_ONLY
class WeatherDescription (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ws.cdyne.com/WeatherWS/}WeatherDescription with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'WeatherDescription')
    _XSDLocation = pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 20, 6)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://ws.cdyne.com/WeatherWS/}WeatherID uses Python identifier WeatherID
    __WeatherID = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'WeatherID'), 'WeatherID', '__httpws_cdyne_comWeatherWS_WeatherDescription_httpws_cdyne_comWeatherWSWeatherID', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 22, 10), )

    
    WeatherID = property(__WeatherID.value, __WeatherID.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}Description uses Python identifier Description
    __Description = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'Description'), 'Description', '__httpws_cdyne_comWeatherWS_WeatherDescription_httpws_cdyne_comWeatherWSDescription', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 23, 10), )

    
    Description = property(__Description.value, __Description.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}PictureURL uses Python identifier PictureURL
    __PictureURL = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'PictureURL'), 'PictureURL', '__httpws_cdyne_comWeatherWS_WeatherDescription_httpws_cdyne_comWeatherWSPictureURL', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 24, 10), )

    
    PictureURL = property(__PictureURL.value, __PictureURL.set, None, None)

    _ElementMap.update({
        __WeatherID.name() : __WeatherID,
        __Description.name() : __Description,
        __PictureURL.name() : __PictureURL
    })
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'WeatherDescription', WeatherDescription)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_2 (pyxb.binding.basis.complexTypeDefinition):
    """Complex type [anonymous] with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 28, 8)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://ws.cdyne.com/WeatherWS/}ZIP uses Python identifier ZIP
    __ZIP = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'ZIP'), 'ZIP', '__httpws_cdyne_comWeatherWS_CTD_ANON_2_httpws_cdyne_comWeatherWSZIP', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 30, 12), )

    
    ZIP = property(__ZIP.value, __ZIP.set, None, None)

    _ElementMap.update({
        __ZIP.name() : __ZIP
    })
    _AttributeMap.update({
        
    })



# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_3 (pyxb.binding.basis.complexTypeDefinition):
    """Complex type [anonymous] with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 35, 8)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://ws.cdyne.com/WeatherWS/}GetCityForecastByZIPResult uses Python identifier GetCityForecastByZIPResult
    __GetCityForecastByZIPResult = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'GetCityForecastByZIPResult'), 'GetCityForecastByZIPResult', '__httpws_cdyne_comWeatherWS_CTD_ANON_3_httpws_cdyne_comWeatherWSGetCityForecastByZIPResult', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 37, 12), )

    
    GetCityForecastByZIPResult = property(__GetCityForecastByZIPResult.value, __GetCityForecastByZIPResult.set, None, None)

    _ElementMap.update({
        __GetCityForecastByZIPResult.name() : __GetCityForecastByZIPResult
    })
    _AttributeMap.update({
        
    })



# Complex type {http://ws.cdyne.com/WeatherWS/}ForecastReturn with content type ELEMENT_ONLY
class ForecastReturn_ (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ws.cdyne.com/WeatherWS/}ForecastReturn with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ForecastReturn')
    _XSDLocation = pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 41, 6)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://ws.cdyne.com/WeatherWS/}Success uses Python identifier Success
    __Success = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'Success'), 'Success', '__httpws_cdyne_comWeatherWS_ForecastReturn__httpws_cdyne_comWeatherWSSuccess', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 43, 10), )

    
    Success = property(__Success.value, __Success.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}ResponseText uses Python identifier ResponseText
    __ResponseText = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'ResponseText'), 'ResponseText', '__httpws_cdyne_comWeatherWS_ForecastReturn__httpws_cdyne_comWeatherWSResponseText', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 44, 10), )

    
    ResponseText = property(__ResponseText.value, __ResponseText.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}State uses Python identifier State
    __State = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'State'), 'State', '__httpws_cdyne_comWeatherWS_ForecastReturn__httpws_cdyne_comWeatherWSState', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 45, 10), )

    
    State = property(__State.value, __State.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}City uses Python identifier City
    __City = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'City'), 'City', '__httpws_cdyne_comWeatherWS_ForecastReturn__httpws_cdyne_comWeatherWSCity', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 46, 10), )

    
    City = property(__City.value, __City.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}WeatherStationCity uses Python identifier WeatherStationCity
    __WeatherStationCity = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'WeatherStationCity'), 'WeatherStationCity', '__httpws_cdyne_comWeatherWS_ForecastReturn__httpws_cdyne_comWeatherWSWeatherStationCity', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 47, 10), )

    
    WeatherStationCity = property(__WeatherStationCity.value, __WeatherStationCity.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}ForecastResult uses Python identifier ForecastResult
    __ForecastResult = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'ForecastResult'), 'ForecastResult', '__httpws_cdyne_comWeatherWS_ForecastReturn__httpws_cdyne_comWeatherWSForecastResult', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 48, 10), )

    
    ForecastResult = property(__ForecastResult.value, __ForecastResult.set, None, None)

    _ElementMap.update({
        __Success.name() : __Success,
        __ResponseText.name() : __ResponseText,
        __State.name() : __State,
        __City.name() : __City,
        __WeatherStationCity.name() : __WeatherStationCity,
        __ForecastResult.name() : __ForecastResult
    })
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ForecastReturn', ForecastReturn_)


# Complex type {http://ws.cdyne.com/WeatherWS/}ArrayOfForecast with content type ELEMENT_ONLY
class ArrayOfForecast (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ws.cdyne.com/WeatherWS/}ArrayOfForecast with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ArrayOfForecast')
    _XSDLocation = pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 51, 6)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://ws.cdyne.com/WeatherWS/}Forecast uses Python identifier Forecast
    __Forecast = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'Forecast'), 'Forecast', '__httpws_cdyne_comWeatherWS_ArrayOfForecast_httpws_cdyne_comWeatherWSForecast', True, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 53, 10), )

    
    Forecast = property(__Forecast.value, __Forecast.set, None, None)

    _ElementMap.update({
        __Forecast.name() : __Forecast
    })
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ArrayOfForecast', ArrayOfForecast)


# Complex type {http://ws.cdyne.com/WeatherWS/}Forecast with content type ELEMENT_ONLY
class Forecast (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ws.cdyne.com/WeatherWS/}Forecast with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'Forecast')
    _XSDLocation = pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 56, 6)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://ws.cdyne.com/WeatherWS/}Date uses Python identifier Date
    __Date = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'Date'), 'Date', '__httpws_cdyne_comWeatherWS_Forecast_httpws_cdyne_comWeatherWSDate', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 58, 10), )

    
    Date = property(__Date.value, __Date.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}WeatherID uses Python identifier WeatherID
    __WeatherID = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'WeatherID'), 'WeatherID', '__httpws_cdyne_comWeatherWS_Forecast_httpws_cdyne_comWeatherWSWeatherID', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 59, 10), )

    
    WeatherID = property(__WeatherID.value, __WeatherID.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}Desciption uses Python identifier Desciption
    __Desciption = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'Desciption'), 'Desciption', '__httpws_cdyne_comWeatherWS_Forecast_httpws_cdyne_comWeatherWSDesciption', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 60, 10), )

    
    Desciption = property(__Desciption.value, __Desciption.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}Temperatures uses Python identifier Temperatures
    __Temperatures = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'Temperatures'), 'Temperatures', '__httpws_cdyne_comWeatherWS_Forecast_httpws_cdyne_comWeatherWSTemperatures', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 61, 10), )

    
    Temperatures = property(__Temperatures.value, __Temperatures.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}ProbabilityOfPrecipiation uses Python identifier ProbabilityOfPrecipiation
    __ProbabilityOfPrecipiation = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'ProbabilityOfPrecipiation'), 'ProbabilityOfPrecipiation', '__httpws_cdyne_comWeatherWS_Forecast_httpws_cdyne_comWeatherWSProbabilityOfPrecipiation', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 62, 10), )

    
    ProbabilityOfPrecipiation = property(__ProbabilityOfPrecipiation.value, __ProbabilityOfPrecipiation.set, None, None)

    _ElementMap.update({
        __Date.name() : __Date,
        __WeatherID.name() : __WeatherID,
        __Desciption.name() : __Desciption,
        __Temperatures.name() : __Temperatures,
        __ProbabilityOfPrecipiation.name() : __ProbabilityOfPrecipiation
    })
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'Forecast', Forecast)


# Complex type {http://ws.cdyne.com/WeatherWS/}temp with content type ELEMENT_ONLY
class temp (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ws.cdyne.com/WeatherWS/}temp with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'temp')
    _XSDLocation = pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 65, 6)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://ws.cdyne.com/WeatherWS/}MorningLow uses Python identifier MorningLow
    __MorningLow = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'MorningLow'), 'MorningLow', '__httpws_cdyne_comWeatherWS_temp_httpws_cdyne_comWeatherWSMorningLow', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 67, 10), )

    
    MorningLow = property(__MorningLow.value, __MorningLow.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}DaytimeHigh uses Python identifier DaytimeHigh
    __DaytimeHigh = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'DaytimeHigh'), 'DaytimeHigh', '__httpws_cdyne_comWeatherWS_temp_httpws_cdyne_comWeatherWSDaytimeHigh', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 68, 10), )

    
    DaytimeHigh = property(__DaytimeHigh.value, __DaytimeHigh.set, None, None)

    _ElementMap.update({
        __MorningLow.name() : __MorningLow,
        __DaytimeHigh.name() : __DaytimeHigh
    })
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'temp', temp)


# Complex type {http://ws.cdyne.com/WeatherWS/}POP with content type ELEMENT_ONLY
class POP (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ws.cdyne.com/WeatherWS/}POP with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'POP')
    _XSDLocation = pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 71, 6)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://ws.cdyne.com/WeatherWS/}Nighttime uses Python identifier Nighttime
    __Nighttime = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'Nighttime'), 'Nighttime', '__httpws_cdyne_comWeatherWS_POP_httpws_cdyne_comWeatherWSNighttime', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 73, 10), )

    
    Nighttime = property(__Nighttime.value, __Nighttime.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}Daytime uses Python identifier Daytime
    __Daytime = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'Daytime'), 'Daytime', '__httpws_cdyne_comWeatherWS_POP_httpws_cdyne_comWeatherWSDaytime', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 74, 10), )

    
    Daytime = property(__Daytime.value, __Daytime.set, None, None)

    _ElementMap.update({
        __Nighttime.name() : __Nighttime,
        __Daytime.name() : __Daytime
    })
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'POP', POP)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_4 (pyxb.binding.basis.complexTypeDefinition):
    """Complex type [anonymous] with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 78, 8)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://ws.cdyne.com/WeatherWS/}ZIP uses Python identifier ZIP
    __ZIP = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'ZIP'), 'ZIP', '__httpws_cdyne_comWeatherWS_CTD_ANON_4_httpws_cdyne_comWeatherWSZIP', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 80, 12), )

    
    ZIP = property(__ZIP.value, __ZIP.set, None, None)

    _ElementMap.update({
        __ZIP.name() : __ZIP
    })
    _AttributeMap.update({
        
    })



# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_5 (pyxb.binding.basis.complexTypeDefinition):
    """Complex type [anonymous] with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 85, 8)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://ws.cdyne.com/WeatherWS/}GetCityWeatherByZIPResult uses Python identifier GetCityWeatherByZIPResult
    __GetCityWeatherByZIPResult = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'GetCityWeatherByZIPResult'), 'GetCityWeatherByZIPResult', '__httpws_cdyne_comWeatherWS_CTD_ANON_5_httpws_cdyne_comWeatherWSGetCityWeatherByZIPResult', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 87, 12), )

    
    GetCityWeatherByZIPResult = property(__GetCityWeatherByZIPResult.value, __GetCityWeatherByZIPResult.set, None, None)

    _ElementMap.update({
        __GetCityWeatherByZIPResult.name() : __GetCityWeatherByZIPResult
    })
    _AttributeMap.update({
        
    })



# Complex type {http://ws.cdyne.com/WeatherWS/}WeatherReturn with content type ELEMENT_ONLY
class WeatherReturn_ (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ws.cdyne.com/WeatherWS/}WeatherReturn with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'WeatherReturn')
    _XSDLocation = pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 91, 6)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://ws.cdyne.com/WeatherWS/}Success uses Python identifier Success
    __Success = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'Success'), 'Success', '__httpws_cdyne_comWeatherWS_WeatherReturn__httpws_cdyne_comWeatherWSSuccess', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 93, 10), )

    
    Success = property(__Success.value, __Success.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}ResponseText uses Python identifier ResponseText
    __ResponseText = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'ResponseText'), 'ResponseText', '__httpws_cdyne_comWeatherWS_WeatherReturn__httpws_cdyne_comWeatherWSResponseText', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 94, 10), )

    
    ResponseText = property(__ResponseText.value, __ResponseText.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}State uses Python identifier State
    __State = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'State'), 'State', '__httpws_cdyne_comWeatherWS_WeatherReturn__httpws_cdyne_comWeatherWSState', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 95, 10), )

    
    State = property(__State.value, __State.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}City uses Python identifier City
    __City = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'City'), 'City', '__httpws_cdyne_comWeatherWS_WeatherReturn__httpws_cdyne_comWeatherWSCity', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 96, 10), )

    
    City = property(__City.value, __City.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}WeatherStationCity uses Python identifier WeatherStationCity
    __WeatherStationCity = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'WeatherStationCity'), 'WeatherStationCity', '__httpws_cdyne_comWeatherWS_WeatherReturn__httpws_cdyne_comWeatherWSWeatherStationCity', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 97, 10), )

    
    WeatherStationCity = property(__WeatherStationCity.value, __WeatherStationCity.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}WeatherID uses Python identifier WeatherID
    __WeatherID = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'WeatherID'), 'WeatherID', '__httpws_cdyne_comWeatherWS_WeatherReturn__httpws_cdyne_comWeatherWSWeatherID', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 98, 10), )

    
    WeatherID = property(__WeatherID.value, __WeatherID.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}Description uses Python identifier Description
    __Description = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'Description'), 'Description', '__httpws_cdyne_comWeatherWS_WeatherReturn__httpws_cdyne_comWeatherWSDescription', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 99, 10), )

    
    Description = property(__Description.value, __Description.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}Temperature uses Python identifier Temperature
    __Temperature = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'Temperature'), 'Temperature', '__httpws_cdyne_comWeatherWS_WeatherReturn__httpws_cdyne_comWeatherWSTemperature', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 100, 10), )

    
    Temperature = property(__Temperature.value, __Temperature.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}RelativeHumidity uses Python identifier RelativeHumidity
    __RelativeHumidity = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'RelativeHumidity'), 'RelativeHumidity', '__httpws_cdyne_comWeatherWS_WeatherReturn__httpws_cdyne_comWeatherWSRelativeHumidity', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 101, 10), )

    
    RelativeHumidity = property(__RelativeHumidity.value, __RelativeHumidity.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}Wind uses Python identifier Wind
    __Wind = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'Wind'), 'Wind', '__httpws_cdyne_comWeatherWS_WeatherReturn__httpws_cdyne_comWeatherWSWind', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 102, 10), )

    
    Wind = property(__Wind.value, __Wind.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}Pressure uses Python identifier Pressure
    __Pressure = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'Pressure'), 'Pressure', '__httpws_cdyne_comWeatherWS_WeatherReturn__httpws_cdyne_comWeatherWSPressure', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 103, 10), )

    
    Pressure = property(__Pressure.value, __Pressure.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}Visibility uses Python identifier Visibility
    __Visibility = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'Visibility'), 'Visibility', '__httpws_cdyne_comWeatherWS_WeatherReturn__httpws_cdyne_comWeatherWSVisibility', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 104, 10), )

    
    Visibility = property(__Visibility.value, __Visibility.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}WindChill uses Python identifier WindChill
    __WindChill = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'WindChill'), 'WindChill', '__httpws_cdyne_comWeatherWS_WeatherReturn__httpws_cdyne_comWeatherWSWindChill', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 105, 10), )

    
    WindChill = property(__WindChill.value, __WindChill.set, None, None)

    
    # Element {http://ws.cdyne.com/WeatherWS/}Remarks uses Python identifier Remarks
    __Remarks = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, u'Remarks'), 'Remarks', '__httpws_cdyne_comWeatherWS_WeatherReturn__httpws_cdyne_comWeatherWSRemarks', False, pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 106, 10), )

    
    Remarks = property(__Remarks.value, __Remarks.set, None, None)

    _ElementMap.update({
        __Success.name() : __Success,
        __ResponseText.name() : __ResponseText,
        __State.name() : __State,
        __City.name() : __City,
        __WeatherStationCity.name() : __WeatherStationCity,
        __WeatherID.name() : __WeatherID,
        __Description.name() : __Description,
        __Temperature.name() : __Temperature,
        __RelativeHumidity.name() : __RelativeHumidity,
        __Wind.name() : __Wind,
        __Pressure.name() : __Pressure,
        __Visibility.name() : __Visibility,
        __WindChill.name() : __WindChill,
        __Remarks.name() : __Remarks
    })
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'WeatherReturn', WeatherReturn_)


GetWeatherInformation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GetWeatherInformation'), CTD_ANON, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 5, 6))
Namespace.addCategoryObject('elementBinding', GetWeatherInformation.name().localName(), GetWeatherInformation)

GetWeatherInformationResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GetWeatherInformationResponse'), CTD_ANON_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 8, 6))
Namespace.addCategoryObject('elementBinding', GetWeatherInformationResponse.name().localName(), GetWeatherInformationResponse)

GetCityForecastByZIP = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GetCityForecastByZIP'), CTD_ANON_2, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 27, 6))
Namespace.addCategoryObject('elementBinding', GetCityForecastByZIP.name().localName(), GetCityForecastByZIP)

GetCityForecastByZIPResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GetCityForecastByZIPResponse'), CTD_ANON_3, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 34, 6))
Namespace.addCategoryObject('elementBinding', GetCityForecastByZIPResponse.name().localName(), GetCityForecastByZIPResponse)

GetCityWeatherByZIP = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GetCityWeatherByZIP'), CTD_ANON_4, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 77, 6))
Namespace.addCategoryObject('elementBinding', GetCityWeatherByZIP.name().localName(), GetCityWeatherByZIP)

GetCityWeatherByZIPResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GetCityWeatherByZIPResponse'), CTD_ANON_5, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 84, 6))
Namespace.addCategoryObject('elementBinding', GetCityWeatherByZIPResponse.name().localName(), GetCityWeatherByZIPResponse)

ArrayOfWeatherDescription = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ArrayOfWeatherDescription'), ArrayOfWeatherDescription_, nillable=pyxb.binding.datatypes.boolean(1), location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 109, 6))
Namespace.addCategoryObject('elementBinding', ArrayOfWeatherDescription.name().localName(), ArrayOfWeatherDescription)

ForecastReturn = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ForecastReturn'), ForecastReturn_, nillable=pyxb.binding.datatypes.boolean(1), location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 110, 6))
Namespace.addCategoryObject('elementBinding', ForecastReturn.name().localName(), ForecastReturn)

WeatherReturn = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'WeatherReturn'), WeatherReturn_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 111, 6))
Namespace.addCategoryObject('elementBinding', WeatherReturn.name().localName(), WeatherReturn)



CTD_ANON_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GetWeatherInformationResult'), ArrayOfWeatherDescription_, scope=CTD_ANON_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 11, 12)))

def _BuildAutomaton ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton
    del _BuildAutomaton
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 11, 12))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'GetWeatherInformationResult')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 11, 12))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
CTD_ANON_._Automaton = _BuildAutomaton()




ArrayOfWeatherDescription_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'WeatherDescription'), WeatherDescription, scope=ArrayOfWeatherDescription_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 17, 10)))

def _BuildAutomaton_ ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_
    del _BuildAutomaton_
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0L, max=None, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 17, 10))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(ArrayOfWeatherDescription_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'WeatherDescription')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 17, 10))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
ArrayOfWeatherDescription_._Automaton = _BuildAutomaton_()




WeatherDescription._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'WeatherID'), pyxb.binding.datatypes.short, scope=WeatherDescription, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 22, 10)))

WeatherDescription._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Description'), pyxb.binding.datatypes.string, scope=WeatherDescription, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 23, 10)))

WeatherDescription._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PictureURL'), pyxb.binding.datatypes.string, scope=WeatherDescription, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 24, 10)))

def _BuildAutomaton_2 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_2
    del _BuildAutomaton_2
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 23, 10))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 24, 10))
    counters.add(cc_1)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(WeatherDescription._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'WeatherID')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 22, 10))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(WeatherDescription._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Description')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 23, 10))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(WeatherDescription._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PictureURL')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 24, 10))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
WeatherDescription._Automaton = _BuildAutomaton_2()




CTD_ANON_2._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ZIP'), pyxb.binding.datatypes.string, scope=CTD_ANON_2, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 30, 12)))

def _BuildAutomaton_3 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_3
    del _BuildAutomaton_3
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 30, 12))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ZIP')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 30, 12))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
CTD_ANON_2._Automaton = _BuildAutomaton_3()




CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GetCityForecastByZIPResult'), ForecastReturn_, scope=CTD_ANON_3, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 37, 12)))

def _BuildAutomaton_4 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_4
    del _BuildAutomaton_4
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 37, 12))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'GetCityForecastByZIPResult')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 37, 12))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
CTD_ANON_3._Automaton = _BuildAutomaton_4()




ForecastReturn_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Success'), pyxb.binding.datatypes.boolean, scope=ForecastReturn_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 43, 10)))

ForecastReturn_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ResponseText'), pyxb.binding.datatypes.string, scope=ForecastReturn_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 44, 10)))

ForecastReturn_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'State'), pyxb.binding.datatypes.string, scope=ForecastReturn_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 45, 10)))

ForecastReturn_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'City'), pyxb.binding.datatypes.string, scope=ForecastReturn_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 46, 10)))

ForecastReturn_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'WeatherStationCity'), pyxb.binding.datatypes.string, scope=ForecastReturn_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 47, 10)))

ForecastReturn_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ForecastResult'), ArrayOfForecast, scope=ForecastReturn_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 48, 10)))

def _BuildAutomaton_5 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_5
    del _BuildAutomaton_5
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 44, 10))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 45, 10))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 46, 10))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 47, 10))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 48, 10))
    counters.add(cc_4)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(ForecastReturn_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Success')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 43, 10))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(ForecastReturn_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ResponseText')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 44, 10))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(ForecastReturn_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'State')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 45, 10))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ForecastReturn_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'City')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 46, 10))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_3, False))
    symbol = pyxb.binding.content.ElementUse(ForecastReturn_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'WeatherStationCity')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 47, 10))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_4, False))
    symbol = pyxb.binding.content.ElementUse(ForecastReturn_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ForecastResult')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 48, 10))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_3, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_3, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_4, True) ]))
    st_5._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
ForecastReturn_._Automaton = _BuildAutomaton_5()




ArrayOfForecast._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Forecast'), Forecast, nillable=pyxb.binding.datatypes.boolean(1), scope=ArrayOfForecast, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 53, 10)))

def _BuildAutomaton_6 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_6
    del _BuildAutomaton_6
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0L, max=None, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 53, 10))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(ArrayOfForecast._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Forecast')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 53, 10))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
ArrayOfForecast._Automaton = _BuildAutomaton_6()




Forecast._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Date'), pyxb.binding.datatypes.dateTime, scope=Forecast, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 58, 10)))

Forecast._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'WeatherID'), pyxb.binding.datatypes.short, scope=Forecast, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 59, 10)))

Forecast._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Desciption'), pyxb.binding.datatypes.string, scope=Forecast, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 60, 10)))

Forecast._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Temperatures'), temp, scope=Forecast, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 61, 10)))

Forecast._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ProbabilityOfPrecipiation'), POP, scope=Forecast, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 62, 10)))

def _BuildAutomaton_7 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_7
    del _BuildAutomaton_7
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 60, 10))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Forecast._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Date')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 58, 10))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Forecast._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'WeatherID')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 59, 10))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Forecast._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Desciption')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 60, 10))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Forecast._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Temperatures')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 61, 10))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(Forecast._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ProbabilityOfPrecipiation')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 62, 10))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    st_4._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
Forecast._Automaton = _BuildAutomaton_7()




temp._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MorningLow'), pyxb.binding.datatypes.string, scope=temp, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 67, 10)))

temp._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DaytimeHigh'), pyxb.binding.datatypes.string, scope=temp, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 68, 10)))

def _BuildAutomaton_8 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_8
    del _BuildAutomaton_8
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 67, 10))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 68, 10))
    counters.add(cc_1)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(temp._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MorningLow')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 67, 10))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(temp._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DaytimeHigh')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 68, 10))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
temp._Automaton = _BuildAutomaton_8()




POP._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Nighttime'), pyxb.binding.datatypes.string, scope=POP, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 73, 10)))

POP._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Daytime'), pyxb.binding.datatypes.string, scope=POP, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 74, 10)))

def _BuildAutomaton_9 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_9
    del _BuildAutomaton_9
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 73, 10))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 74, 10))
    counters.add(cc_1)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(POP._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Nighttime')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 73, 10))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(POP._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Daytime')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 74, 10))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
POP._Automaton = _BuildAutomaton_9()




CTD_ANON_4._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ZIP'), pyxb.binding.datatypes.string, scope=CTD_ANON_4, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 80, 12)))

def _BuildAutomaton_10 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_10
    del _BuildAutomaton_10
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 80, 12))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_4._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ZIP')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 80, 12))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
CTD_ANON_4._Automaton = _BuildAutomaton_10()




CTD_ANON_5._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GetCityWeatherByZIPResult'), WeatherReturn_, scope=CTD_ANON_5, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 87, 12)))

def _BuildAutomaton_11 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_11
    del _BuildAutomaton_11
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_5._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'GetCityWeatherByZIPResult')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 87, 12))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CTD_ANON_5._Automaton = _BuildAutomaton_11()




WeatherReturn_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Success'), pyxb.binding.datatypes.boolean, scope=WeatherReturn_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 93, 10)))

WeatherReturn_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ResponseText'), pyxb.binding.datatypes.string, scope=WeatherReturn_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 94, 10)))

WeatherReturn_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'State'), pyxb.binding.datatypes.string, scope=WeatherReturn_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 95, 10)))

WeatherReturn_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'City'), pyxb.binding.datatypes.string, scope=WeatherReturn_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 96, 10)))

WeatherReturn_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'WeatherStationCity'), pyxb.binding.datatypes.string, scope=WeatherReturn_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 97, 10)))

WeatherReturn_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'WeatherID'), pyxb.binding.datatypes.short, scope=WeatherReturn_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 98, 10)))

WeatherReturn_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Description'), pyxb.binding.datatypes.string, scope=WeatherReturn_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 99, 10)))

WeatherReturn_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Temperature'), pyxb.binding.datatypes.string, scope=WeatherReturn_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 100, 10)))

WeatherReturn_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RelativeHumidity'), pyxb.binding.datatypes.string, scope=WeatherReturn_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 101, 10)))

WeatherReturn_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Wind'), pyxb.binding.datatypes.string, scope=WeatherReturn_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 102, 10)))

WeatherReturn_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Pressure'), pyxb.binding.datatypes.string, scope=WeatherReturn_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 103, 10)))

WeatherReturn_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Visibility'), pyxb.binding.datatypes.string, scope=WeatherReturn_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 104, 10)))

WeatherReturn_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'WindChill'), pyxb.binding.datatypes.string, scope=WeatherReturn_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 105, 10)))

WeatherReturn_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Remarks'), pyxb.binding.datatypes.string, scope=WeatherReturn_, location=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 106, 10)))

def _BuildAutomaton_12 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_12
    del _BuildAutomaton_12
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 94, 10))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 95, 10))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 96, 10))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 97, 10))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 99, 10))
    counters.add(cc_4)
    cc_5 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 100, 10))
    counters.add(cc_5)
    cc_6 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 101, 10))
    counters.add(cc_6)
    cc_7 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 102, 10))
    counters.add(cc_7)
    cc_8 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 103, 10))
    counters.add(cc_8)
    cc_9 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 104, 10))
    counters.add(cc_9)
    cc_10 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 105, 10))
    counters.add(cc_10)
    cc_11 = fac.CounterCondition(min=0L, max=1L, metadata=pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 106, 10))
    counters.add(cc_11)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(WeatherReturn_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Success')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 93, 10))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(WeatherReturn_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ResponseText')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 94, 10))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(WeatherReturn_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'State')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 95, 10))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(WeatherReturn_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'City')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 96, 10))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(WeatherReturn_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'WeatherStationCity')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 97, 10))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(WeatherReturn_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'WeatherID')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 98, 10))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_4, False))
    symbol = pyxb.binding.content.ElementUse(WeatherReturn_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Description')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 99, 10))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_5, False))
    symbol = pyxb.binding.content.ElementUse(WeatherReturn_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Temperature')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 100, 10))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_6, False))
    symbol = pyxb.binding.content.ElementUse(WeatherReturn_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RelativeHumidity')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 101, 10))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_7, False))
    symbol = pyxb.binding.content.ElementUse(WeatherReturn_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Wind')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 102, 10))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_8, False))
    symbol = pyxb.binding.content.ElementUse(WeatherReturn_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Pressure')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 103, 10))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_9, False))
    symbol = pyxb.binding.content.ElementUse(WeatherReturn_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Visibility')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 104, 10))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_10, False))
    symbol = pyxb.binding.content.ElementUse(WeatherReturn_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'WindChill')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 105, 10))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_11, False))
    symbol = pyxb.binding.content.ElementUse(WeatherReturn_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Remarks')), pyxb.utils.utility.Location('http://wsf.cdyne.com/WeatherWS/Weather.asmx?WSDL', 106, 10))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_3, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_3, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    transitions.append(fac.Transition(st_7, [
         ]))
    transitions.append(fac.Transition(st_8, [
         ]))
    transitions.append(fac.Transition(st_9, [
         ]))
    transitions.append(fac.Transition(st_10, [
         ]))
    transitions.append(fac.Transition(st_11, [
         ]))
    transitions.append(fac.Transition(st_12, [
         ]))
    transitions.append(fac.Transition(st_13, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_4, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_4, False) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_5, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_5, False) ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_6, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_6, False) ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_7, False) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_8, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_8, False) ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_9, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_9, False) ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_10, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_10, False) ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_11, True) ]))
    st_13._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
WeatherReturn_._Automaton = _BuildAutomaton_12()

