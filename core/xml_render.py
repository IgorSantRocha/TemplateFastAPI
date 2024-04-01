import os
from lxml import etree
from lxml import objectify
from jinja2 import Environment, FileSystemLoader
import core.filters as filters


class XmlRender:

    @classmethod
    async def recursively_normalize(cls, vals):
        for item in vals:
            if type(vals[item]) is str:
                vals[item] = vals[item].strip()
                vals[item] = filters.normalize_str(vals[item])
            elif type(vals[item]) is dict:
                await cls.recursively_normalize(vals[item])
            elif type(vals[item]) is list:
                for a in vals[item]:
                    await cls.recursively_normalize(a)
        return vals

    @classmethod
    async def recursively_normalize_mult(cls, vals):
        if vals is None:
            return vals

        for item in vals:
            if isinstance(item, dict):  # Verifica se o item é um dicionário
                # Chama recursivamente a função com o dicionário
                await cls.recursively_normalize_mult(item)
            elif isinstance(item, list):  # Verifica se o item é uma lista
                for a in item:
                    # Chama recursivamente a função com o item da lista
                    await cls.recursively_normalize_mult(a)

        return vals

    @classmethod
    async def _render(cls, method, **kwargs):
        path = os.path.join(os.path.dirname(__file__), 'templates')
        xml_send = await cls.render_xml(path, '%s.xml' % method, **kwargs)
        return xml_send.encode('utf-8')

    @classmethod
    async def render_xml(cls, path, template_name, **banklisp):
        banklisp = await cls.recursively_normalize(banklisp)
        env = Environment(
            loader=FileSystemLoader(path))
        env.filters["normalize"] = filters.strip_line_feed
        env.filters["normalize_str"] = filters.normalize_str
        env.filters["format_percent"] = filters.format_percent
        env.filters["format_datetime"] = filters.format_datetime
        env.filters["format_date"] = filters.format_date
        env.filters["comma"] = filters.format_with_comma
        template = env.get_template(template_name)
        banklisp = cls.escape(str_xml=banklisp)
        xml = template.render(**banklisp)
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True,
                                 strip_cdata=False)
        root = etree.fromstring(xml, parser=parser)
        for element in root.iter("*"):  # remove espaços em branco
            if element.text is not None and not element.text.strip():
                element.text = None
        return etree.tostring(root, encoding=str)

    @classmethod
    async def _render_mult(cls, method, headers, items, **kwargs):
        path = os.path.join(os.path.dirname(__file__), 'templates')
        # Aguarda a normalização dos items
        normalized_items = await cls.recursively_normalize_mult(items)
        xml_send = await cls.render_xml(path, '%s.xml' % method, headers=headers, items=normalized_items, **kwargs)
        return xml_send

    @classmethod
    async def sanitize_response(cls, response):
        parser = etree.XMLParser(encoding='utf-8')
        tree = etree.fromstring(response.encode('UTF-8'), parser=parser)
        # Remove namespaces inuteis na resposta
        for elem in tree.getiterator():
            if not hasattr(elem.tag, 'find'):
                continue
            i = elem.tag.find('}')
            if i >= 0:
                elem.tag = elem.tag[i + 1:]
        objectify.deannotate(tree, cleanup_namespaces=True)
        return response, objectify.fromstring(etree.tostring(tree))

    @classmethod
    def escape(cls, str_xml):
        for key in list(str_xml):
            if type(str_xml[key]) == str:
                str_xml[key] = str_xml[key].replace("&", "&amp;")
                str_xml[key] = str_xml[key].replace("<", "&lt;")
                str_xml[key] = str_xml[key].replace(">", "&gt;")
                str_xml[key] = str_xml[key].replace("\"", "&quot;")
                str_xml[key] = str_xml[key].replace("'", "&apos;")
        return str_xml
