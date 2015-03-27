# XML namespaces #

http://www.w3schools.com/xml/xml_namespaces.asp

based on mailing list topics [here](https://groups.google.com/forum/#!topic/botsmail/PtAjn6QApy4) and [here](https://code.google.com/p/bots/w/edit/XMLnamespace)

Dealing with xml namespaces can be a bit difficult in Bots. They can greatly complicate grammars and mappings. Often your EDI partner will want to send or receive XML with namespaces, but actually Bots does not need (or want) them as there are rarely any naming conflicts within a single XML file!

Where an XML file has only one namespace, usually the "default" namespace is used.<br>
eg. <code>xmlns="schemas-hiwg-org-au:EnvelopeV1.0</code>

If the file has multiple namespaces, then namespace prefixes are used. These prefixes can be any value.<br>
eg. <code>xmlns:ENV="schemas-hiwg-org-au:EnvelopeV1.0"</code>

There are several ways to deal with namespaces in Bots:<br>
<br>
<h2>1. Ignore incoming XML namespace</h2>
For incoming XML files that are to be mapped into something else, you probably don't need the namespaces at all. In my opinion this is the "best" way. See <a href='https://code.google.com/p/bots/wiki/RouteScriptsExample?ts=1415698918&updated=RouteScriptsExample#Example_7:_Preprocessing_to_ignore/remove_XML_namespaces'>Ignore incoming XML namespace</a>

<h2>2. Use incoming XML namespace</h2>
When a namespace must be used, it is needed in many places (structure, recorddefs, mapping) but you want to specify the namespace string, which can be quite long, only in one place. This has several benefits:<br>
<ul><li>If it needs to change, this is easy to do in one place only<br>
</li><li>grammar and mapping will be smaller, and look neater</li></ul>

For example, the incoming XML file may look like ...<br>
<pre><code>&lt;?xml version="1.0"?&gt;<br>
&lt;Orders xmlns:xsd="http://www.w3.org/2001/XMLSchema"<br>
     xmlns="http://www.company.com/EDIOrders"<br>
     targetNamespace="http//www.company.com/EDIOrders"&gt;<br>
      &lt;Order&gt;<br>
        &lt;OrderNumber&gt;239062415&lt;/OrderNumber&gt;<br>
        &lt;DateOrdered&gt;2014-02-24&lt;/DateOrdered&gt;<br>
        &lt;LineCount&gt;10&lt;/LineCount&gt;<br>
etc...<br>
</code></pre>

If you created your grammar with xml2botsgrammar, it probably has the namespace repeated over and over in structure and recorddefs, like this...<br>
<pre><code>structure=    [<br>
{ID:'{http://www.company.com/EDIOrders}Orders',MIN:1,MAX:1,LEVEL:[<br>
    {ID:'{http://www.company.com/EDIOrders}Order',MIN:1,MAX:99999,<br>
        QUERIES:{<br>
             'botskey':      {'BOTSID':'{http://www.company.com/EDIOrders}Order','{http://www.company.com/EDIOrders}OrderNumber':None},<br>
            },<br>
        LEVEL:[<br>
        {ID:'{http://www.company.com/EDIOrders}OrderItems',MIN:0,MAX:1,LEVEL:[<br>
            {ID:'{http://www.company.com/EDIOrders}OrderLine',MIN:1,MAX:99999},<br>
            ]},<br>
        ]},<br>
    ]}<br>
]<br>
<br>
recorddefs = {<br>
   '{http://www.company.com/EDIOrders}Orders':[<br>
            ['BOTSID','M',256,'A'],<br>
            ['{http://www.company.com/EDIOrders}Orders__targetNamespace','C',256,'AN'],<br>
          ],<br>
   '{http://www.company.com/EDIOrders}Order':[<br>
            ['BOTSID','M',256,'A'],<br>
            ['{http://www.company.com/EDIOrders}OrderNumber','C', 20,'AN'],<br>
            ['{http://www.company.com/EDIOrders}DateOrdered','C', 10,'AN'],<br>
            ['{http://www.company.com/EDIOrders}LineCount','C', 5,'R'],<br>
<br>
# etc...<br>
</code></pre>

So, we want to improve this. In your grammar, first add the namespace as a string constant. This is the only place it should be specified, and everywhere else refers to it.<br>
<br>
Note: If the XML has multiple namespaces, you can use the same technique and just add more constants (xmlns1, xmlns2, etc).<br>
<pre><code>xmlns='{http://www.company.com/EDIOrders}'<br>
</code></pre>

Also include it in the syntax dict. This allows us to reference it later in mappings.<br>
<pre><code>syntax = {<br>
        'xmlns':xmlns,<br>
}<br>
</code></pre>


In your grammar, replace all instances of the namespace string with the constant, so it looks like this...<br>
<pre><code>structure=    [<br>
{ID:xmlns+'Orders',MIN:1,MAX:1,LEVEL:[<br>
    {ID:xmlns+'Order',MIN:1,MAX:99999,<br>
        QUERIES:{<br>
             'botskey':      {'BOTSID':xmlns+'Order',xmlns+'OrderNumber':None},<br>
            },<br>
        LEVEL:[<br>
        {ID:xmlns+'OrderItems',MIN:0,MAX:1,LEVEL:[<br>
            {ID:xmlns+'OrderLine',MIN:1,MAX:99999},<br>
            ]},<br>
        ]},<br>
    ]}<br>
]<br>
<br>
recorddefs = {<br>
   xmlns+'Orders':[<br>
            ['BOTSID','M',256,'A'],<br>
            [xmlns+'Orders__targetNamespace','C',256,'AN'],<br>
          ],<br>
   xmlns+'Order':[<br>
            ['BOTSID','M',256,'A'],<br>
            [xmlns+'OrderNumber','C', 20,'AN'],<br>
            [xmlns+'DateOrdered','C', 10,'AN'],<br>
            [xmlns+'LineCount','C', 5,'R'],<br>
<br>
# etc...<br>
</code></pre>

Now in the mapping script, read the xmlns value from grammar.<br>
<pre><code>import bots.grammar as grammar<br>
<br>
    xmlns = grammar.grammarread('xml',inn.ta_info['messagetype']).syntax['xmlns']<br>
</code></pre>

Then use it wherever needed in the mapping, like this...<br>
<pre><code>    # Get OrderNumber from XML with namespace<br>
    OrderNumber = inn.get({'BOTSID':xmlns+'Order',xmlns+'OrderNumber':None})<br>
</code></pre>

<h2>3. Outgoing XML with only a default namespace</h2>

This can be done by defining xmlns as a tag, and setting it in mapping.<br>
<br>
TODO: provide example<br>
<br>
<h2>4. Outgoing XML with default namespace prefixes</h2>

By default, Bots will use the namespace prefixes ns0, ns1, etc. The actual prefix used is unimportant to XML meaning.<br>
<br>
TODO: provide example<br>
<br>
<h2>5. Outgoing XML with specific namespace prefixes</h2>

Your EDI partner may request a specific namespace prefix be used; This is technically un-necessary and bad design, but they may insist on it anyway!<br>
<br>
TODO: provide example