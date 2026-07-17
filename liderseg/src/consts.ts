export const SITE = {
  name: 'Liderseg',
  title: 'Receba sua Indenização em caso de Acidente | Liderseg',
  description:
    'Sofreu um acidente? Você pode ter direito a até R$ 100 mil de indenização: Seguro RCF, DPVAT, Seguro de Vida, Auxílio-Acidente e Auxílio-Doença. Fale com um especialista da Liderseg no WhatsApp — você só paga se receber.',
  cnpj: '11.331.853/0001-22',
  phoneDisplay: '(62) 3514-4250',
  phone: '556235144250',
  privacyUrl: '/politica-de-privacidade',
  instagram: 'liderseg_indenizacoes',
};

const DEFAULT_MESSAGE =
  'Olá! Sofri um acidente e quero falar com um especialista sobre meus direitos à indenização.';

export function whatsappLink(message: string = DEFAULT_MESSAGE): string {
  return `https://wa.me/${SITE.phone}?text=${encodeURIComponent(message)}`;
}

export const WHATSAPP_DEFAULT = whatsappLink();
