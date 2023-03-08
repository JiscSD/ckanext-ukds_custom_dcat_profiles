// Enable JavaScript's strict mode. Strict mode catches some common
// programming errors and throws exceptions, prevents some unsafe actions from
// being taken, and disables some confusing and bad JavaScript features.
"use strict";

ckan.module('ukds_cdp_popover_info', function ($)
{
  return {
    initialize: function ()
    {
      //We only go through the popover creation if "type" and "title" are available.
      if (!!this.options.type && !!this.options.title)
      {
        let content;
        let html = false;

        switch (this.options.type) {
          case "MRD_info":

              //For the Machine-readable data header, we provide an html content.
              content = `
                <span>Machine readable data is data structured in a format that can be understood and processed by a computer.
                Here we provide a number of file formats for machine processing:</span>
                <br/>
                <ul>
                  <li>
                    <span><b>API</b> - The CKAN native RPC-style Action API that generates JSON data in CKAN native format. For more information please visit the <a href="https://docs.ckan.org/en/latest/api/index.html" target="_blank">guide</a></span>
                  </li>
                  <li>
                    <span><b>RDF</b> - The Resource Description Framework (RDF) format is a standard for description of interchanging data. It is served in different syntaxes including XML, Turtle, Notation3 and JSON-LD.</span>
                  </li>
                </ul>
              `;
              html = true;
            break;
          default:
            break;
        }


        this.el.popover({title:this.options.title,
          content: content,
          html : html,
          placement: 'right'});

      }
    }
  };
});