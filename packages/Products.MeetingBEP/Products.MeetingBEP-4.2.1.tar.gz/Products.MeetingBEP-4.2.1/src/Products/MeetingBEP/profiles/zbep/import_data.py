# -*- coding: utf-8 -*-

from copy import deepcopy
from Products.MeetingCommunes.profiles.examples_fr import import_data as examples_fr_import_data
from Products.MeetingCommunes.profiles.simple import import_data as simple_import_data
from Products.PloneMeeting.profiles import AnnexTypeDescriptor
from Products.PloneMeeting.profiles import CategoryDescriptor
from Products.PloneMeeting.profiles import ItemAnnexTypeDescriptor
from Products.PloneMeeting.profiles import MeetingConfigDescriptor
from Products.PloneMeeting.profiles import OrgDescriptor
from Products.PloneMeeting.profiles import PloneGroupDescriptor
from Products.PloneMeeting.profiles import PloneMeetingConfiguration
from Products.PloneMeeting.profiles import PodTemplateDescriptor
from Products.PloneMeeting.profiles import UserDescriptor


# File types -------------------------------------------------------------------
annexe = ItemAnnexTypeDescriptor('annexe', 'Annexe', u'attach.png')
annexeDecision = ItemAnnexTypeDescriptor('annexeDecision', 'Annexe à la décision', u'attach.png',
                                         relatedTo='item_decision')
annexeAvis = AnnexTypeDescriptor('annexeAvis', 'Annexe à un avis', u'attach.png',
                                 relatedTo='advice')
annexeSeance = AnnexTypeDescriptor('annexe', 'Annexe', u'attach.png', relatedTo='meeting')

# Categories -------------------------------------------------------------------
categories = [
    CategoryDescriptor('approbation-pv',
                       "Approbation du procès verbal de la dernière réunion",
                       category_id='1',
                       using_groups=['dirgen', 'secretariat']),
    CategoryDescriptor('decision',
                       "Décision",
                       category_id='2'),
    CategoryDescriptor('communication',
                       "Communication",
                       category_id='3'),
]

# Pod templates ----------------------------------------------------------------
agendaTemplate = PodTemplateDescriptor('oj', 'Ordre du jour')
agendaTemplate.is_reusable = True
agendaTemplate.odt_file = 'ordredujour.odt'
agendaTemplate.pod_formats = ['odt', 'pdf', ]
agendaTemplate.pod_portal_types = ['Meeting']
agendaTemplate.tal_condition = u'python:tool.isManager(here)'
agendaTemplate.style_template = ['styles1']

decisionsTemplate = PodTemplateDescriptor('pv', 'Procès-verbal')
decisionsTemplate.is_reusable = True
decisionsTemplate.odt_file = 'proces-verbal.odt'
decisionsTemplate.pod_formats = ['odt', 'pdf', ]
decisionsTemplate.pod_portal_types = ['Meeting']
decisionsTemplate.tal_condition = u'python:tool.isManager(here)'
decisionsTemplate.style_template = ['styles1']

noteTravailTemplate = PodTemplateDescriptor('note-travail', 'Note de travail')
noteTravailTemplate.is_reusable = True
noteTravailTemplate.odt_file = 'notedetravail.odt'
noteTravailTemplate.pod_formats = ['odt', 'pdf', ]
noteTravailTemplate.pod_portal_types = ['MeetingItem']
noteTravailTemplate.style_template = ['styles1']

extraitPVTemplate = PodTemplateDescriptor('extrait-pv', 'Extrait PV')
extraitPVTemplate.is_reusable = True
extraitPVTemplate.odt_file = 'extraitpv.odt'
extraitPVTemplate.pod_formats = ['odt', 'pdf', ]
extraitPVTemplate.pod_portal_types = ['MeetingItem']
extraitPVTemplate.tal_condition = u'python:tool.isManager(here)'
extraitPVTemplate.style_template = ['styles1']

templates = [agendaTemplate, decisionsTemplate, noteTravailTemplate, extraitPVTemplate]

reuseAgendaTemplate = PodTemplateDescriptor('oj', 'Ordre du jour')
reuseAgendaTemplate.pod_template_to_use = {'cfg_id': 'bep-ca', 'template_id': 'oj'}
reuseAgendaTemplate.pod_formats = ['odt', 'pdf', ]
reuseAgendaTemplate.pod_portal_types = ['Meeting']
reuseAgendaTemplate.tal_condition = u'python:tool.isManager(here)'

reuseDecisionsTemplate = PodTemplateDescriptor('pv', 'Procès-verbal')
reuseDecisionsTemplate.pod_template_to_use = {'cfg_id': 'bep-ca', 'template_id': 'pv'}
reuseDecisionsTemplate.pod_formats = ['odt', 'pdf', ]
reuseDecisionsTemplate.pod_portal_types = ['Meeting']
reuseDecisionsTemplate.tal_condition = u'python:tool.isManager(here)'

reuseNoteTravailTemplate = PodTemplateDescriptor('note-travail', 'Note de travail')
reuseNoteTravailTemplate.pod_template_to_use = {'cfg_id': 'bep-ca', 'template_id': 'note-travail'}
reuseNoteTravailTemplate.pod_formats = ['odt', 'pdf', ]
reuseNoteTravailTemplate.pod_portal_types = ['MeetingItem']

reuseExtraitPVTemplate = PodTemplateDescriptor('extrait-pv', 'Extrait PV')
reuseExtraitPVTemplate.pod_template_to_use = {'cfg_id': 'bep-ca', 'template_id': 'extrait-pv'}
reuseExtraitPVTemplate.pod_formats = ['odt', 'pdf', ]
reuseExtraitPVTemplate.pod_portal_types = ['MeetingItem']
reuseExtraitPVTemplate.tal_condition = u'python:tool.isManager(here)'

reuse_templates = [reuseAgendaTemplate, reuseDecisionsTemplate,
                   reuseNoteTravailTemplate, reuseExtraitPVTemplate]

# Users ------------------------------------------------------------------------
ajo = UserDescriptor('ajo', [], email="ajo@bep.be", fullname="Amélie JOLY")
cbo = UserDescriptor('cbo', [], email="cbo@bep.be", fullname="Charlotte BOUILLET")
dlo = UserDescriptor('dlo', [], email="dlo@bep.be", fullname="David LONGFILS")
dma = UserDescriptor('dma', [], email="dma@bep.be", fullname="Delphine MAROT")
dde = UserDescriptor('dde', [], email="dde@bep.be", fullname="Dominique DETHY")
ebe = UserDescriptor('ebe', [], email="ebe@bep.be", fullname="Elisabeth BOIS D'ENGHIEN")
fma = UserDescriptor('fma', [], email="fma@bep.be", fullname="Frédéric MASSON")
gqu = UserDescriptor('gqu', [], email="gqu@bep.be", fullname="Geoffroy QUENON")
ito = UserDescriptor('ito', [], email="ito@bep.be", fullname="Imane TORY")
ibe = UserDescriptor('ibe', [], email="ibe@bep.be", fullname="Ingrid BERTRAND")
jyp = UserDescriptor('jyp', [], email="jyp@bep.be", fullname="Jean-Yves PAGES")
jpo = UserDescriptor('jpo', [], email="jpo@bep.be", fullname="Julien PONCELET")
jca = UserDescriptor('jca', [], email="jca@bep.be", fullname="Justine CAVILLOT")
lgo = UserDescriptor('lgo', [], email="lgo@bep.be", fullname="Laurence GOURGUE")
mdh = UserDescriptor('mdh', [], email="mdh@bep.be", fullname="Marc DEHARENG")
mdr = UserDescriptor('mdr', [], email="mdr@bep.be", fullname="Marc DERROITTE")
mdu = UserDescriptor('mdu', [], email="mdu@bep.be", fullname="Marie DUPONT")
nvg = UserDescriptor('nvg', [], email="nvg@bep.be", fullname="Nathalie VAN GOEY ")
ogr = UserDescriptor('ogr', [], email="ogr@bep.be", fullname="Olivier GRANVILLE")
pli = UserDescriptor('pli', [], email="pli@bep.be", fullname="Pascal LIBOIS")
qox = UserDescriptor('qox', [], email="qox@bep.be", fullname="Quentin ORBAN DE XIVRY")
rde = UserDescriptor('rde', [], email="rde@bep.be", fullname="Renaud DEGUELDRE")
sbr = UserDescriptor('sbr', [], email="sbr@bep.be", fullname="Sébastien BOURGEOIS")
str_user = UserDescriptor('str', [], email="str@bep.be", fullname="Sébastien TRIFFOY")
sma = UserDescriptor('sma', [], email="sma@bep.be", fullname="Sophie MARLET")
the = UserDescriptor('the', [], email="the@bep.be", fullname="Tom HEURION")
isa = UserDescriptor('isa', [], email="isa@bep.be", fullname="Isabelle SADIN")
assembly_member = UserDescriptor('assembly_member', [], email="test@test.be", fullname="Assembly Member")

# Groups -----------------------------------------------------------------------
dg_org = OrgDescriptor('dirgen', u'Direction Générale', u'DG')
sg_org = OrgDescriptor('secretariat', u'Secrétariat Général', u'SECGEN')
sgcs_org = OrgDescriptor('secretariat-general-chef-de-service',
                         u'Secrétariat Général (Chef de service)',
                         u'SECGEN (chef de service)')
com_org = OrgDescriptor('communication', u'Communication & Web', u'COM')
comcs_org = OrgDescriptor('communication-web-chef-de-service',
                          u'Communication & Web (Chef de service)',
                          u'Com & Web (chef)')
jur_org = OrgDescriptor('service-juridique', u'Service Juridique', u'JUR')
jur_org.item_advice_states = [
    u'bep-ca__state__validated',
    u'bep-ca__state__presented',
    u'bep-audit__state__validated',
    u'bep-audit__state__presented',
    u'bep-remun__state__validated',
    u'bep-remun__state__presented',
    u'bep-ag__state__validated',
    u'bep-ag__state__presented',
    u'expa-ca__state__validated',
    u'expa-ca__state__presented',
    u'expa-audit__state__validated',
    u'expa-audit__state__presented',
    u'expa-remun__state__validated',
    u'expa-remun__state__presented',
    u'expa-ag__state__validated',
    u'expa-ag__state__presented',
    u'enviro-ca__state__validated',
    u'enviro-ca__state__presented',
    u'enviro-audit__state__validated',
    u'enviro-audit__state__presented',
    u'enviro-remun__state__validated',
    u'enviro-remun__state__presented',
    u'enviro-ag__state__validated',
    u'enviro-ag__state__presented',
    u'crema-ca__state__validated',
    u'crema-ca__state__presented',
    u'crema-audit__state__validated',
    u'crema-audit__state__presented',
    u'crema-remun__state__validated',
    u'crema-remun__state__presented',
    u'crema-ag__state__validated',
    u'crema-ag__state__presented',
    u'idefin-ca__state__validated',
    u'idefin-ca__state__presented',
    u'idefin-audit__state__validated',
    u'idefin-audit__state__presented',
    u'idefin-remun__state__validated',
    u'idefin-remun__state__presented',
    u'idefin-ag__state__validated',
    u'idefin-ag__state__presented']
jur_org.item_advice_edit_states = jur_org.item_advice_states
jur_org.item_advice_view_states = [
    u'bep-ca__state__accepted_out_of_meeting',
    u'bep-ca__state__validated',
    u'bep-ca__state__presented',
    u'bep-ca__state__delayed',
    u'bep-ca__state__pre_accepted',
    u'bep-ca__state__itemfrozen',
    u'bep-ca__state__accepted_out_of_meeting_emergency',
    u'bep-ca__state__refused',
    u'bep-ca__state__accepted',
    u'bep-ca__state__accepted_but_modified',
    u'bep-audit__state__accepted',
    u'bep-audit__state__validated', u'bep-audit__state__presented',
    u'bep-audit__state__delayed', u'bep-audit__state__pre_accepted',
    u'bep-audit__state__itemfrozen',
    u'bep-audit__state__accepted_out_of_meeting_emergency',
    u'bep-audit__state__accepted_but_modified',
    u'bep-audit__state__accepted_out_of_meeting', u'bep-audit__state__refused',
    u'bep-remun__state__accepted', u'bep-remun__state__validated',
    u'bep-remun__state__presented', u'bep-remun__state__delayed',
    u'bep-remun__state__pre_accepted', u'bep-remun__state__itemfrozen',
    u'bep-remun__state__accepted_out_of_meeting_emergency',
    u'bep-remun__state__accepted_but_modified',
    u'bep-remun__state__accepted_out_of_meeting', u'bep-remun__state__refused',
    u'bep-ag__state__accepted', u'bep-ag__state__validated',
    u'bep-ag__state__presented', u'bep-ag__state__delayed',
    u'bep-ag__state__pre_accepted', u'bep-ag__state__itemfrozen',
    u'bep-ag__state__accepted_out_of_meeting_emergency',
    u'bep-ag__state__accepted_but_modified',
    u'bep-ag__state__accepted_out_of_meeting', u'bep-ag__state__refused',
    u'expa-ca__state__accepted', u'expa-ca__state__validated',
    u'expa-ca__state__presented', u'expa-ca__state__delayed',
    u'expa-ca__state__pre_accepted', u'expa-ca__state__itemfrozen',
    u'expa-ca__state__accepted_out_of_meeting_emergency',
    u'expa-ca__state__accepted_but_modified',
    u'expa-ca__state__accepted_out_of_meeting', u'expa-ca__state__refused',
    u'expa-audit__state__accepted', u'expa-audit__state__validated',
    u'expa-audit__state__presented', u'expa-audit__state__delayed',
    u'expa-audit__state__pre_accepted', u'expa-audit__state__itemfrozen',
    u'expa-audit__state__accepted_out_of_meeting_emergency',
    u'expa-audit__state__accepted_but_modified',
    u'expa-audit__state__accepted_out_of_meeting',
    u'expa-audit__state__refused', u'expa-remun__state__accepted',
    u'expa-remun__state__validated', u'expa-remun__state__presented',
    u'expa-remun__state__delayed', u'expa-remun__state__pre_accepted',
    u'expa-remun__state__itemfrozen',
    u'expa-remun__state__accepted_out_of_meeting_emergency',
    u'expa-remun__state__accepted_but_modified',
    u'expa-remun__state__accepted_out_of_meeting',
    u'expa-remun__state__refused', u'expa-ag__state__accepted',
    u'expa-ag__state__validated', u'expa-ag__state__presented',
    u'expa-ag__state__delayed', u'expa-ag__state__pre_accepted',
    u'expa-ag__state__itemfrozen',
    u'expa-ag__state__accepted_out_of_meeting_emergency',
    u'expa-ag__state__accepted_but_modified',
    u'expa-ag__state__accepted_out_of_meeting', u'expa-ag__state__refused',
    u'enviro-ca__state__accepted', u'enviro-ca__state__validated',
    u'enviro-ca__state__presented', u'enviro-ca__state__delayed',
    u'enviro-ca__state__pre_accepted', u'enviro-ca__state__itemfrozen',
    u'enviro-ca__state__accepted_out_of_meeting_emergency',
    u'enviro-ca__state__accepted_but_modified',
    u'enviro-ca__state__accepted_out_of_meeting', u'enviro-ca__state__refused',
    u'enviro-audit__state__accepted', u'enviro-audit__state__validated',
    u'enviro-audit__state__presented', u'enviro-audit__state__delayed',
    u'enviro-audit__state__pre_accepted', u'enviro-audit__state__itemfrozen',
    u'enviro-audit__state__accepted_out_of_meeting_emergency',
    u'enviro-audit__state__accepted_but_modified',
    u'enviro-audit__state__accepted_out_of_meeting',
    u'enviro-audit__state__refused', u'enviro-remun__state__accepted',
    u'enviro-remun__state__validated', u'enviro-remun__state__presented',
    u'enviro-remun__state__delayed', u'enviro-remun__state__pre_accepted',
    u'enviro-remun__state__itemfrozen',
    u'enviro-remun__state__accepted_out_of_meeting_emergency',
    u'enviro-remun__state__accepted_but_modified',
    u'enviro-remun__state__accepted_out_of_meeting',
    u'enviro-remun__state__refused', u'enviro-ag__state__accepted',
    u'enviro-ag__state__validated', u'enviro-ag__state__presented',
    u'enviro-ag__state__delayed', u'enviro-ag__state__pre_accepted',
    u'enviro-ag__state__itemfrozen',
    u'enviro-ag__state__accepted_out_of_meeting_emergency',
    u'enviro-ag__state__accepted_but_modified',
    u'enviro-ag__state__accepted_out_of_meeting', u'enviro-ag__state__refused',
    u'crema-ca__state__accepted', u'crema-ca__state__validated',
    u'crema-ca__state__presented', u'crema-ca__state__delayed',
    u'crema-ca__state__pre_accepted', u'crema-ca__state__itemfrozen',
    u'crema-ca__state__accepted_out_of_meeting_emergency',
    u'crema-ca__state__accepted_but_modified',
    u'crema-ca__state__accepted_out_of_meeting', u'crema-ca__state__refused',
    u'crema-audit__state__accepted', u'crema-audit__state__validated',
    u'crema-audit__state__presented', u'crema-audit__state__delayed',
    u'crema-audit__state__pre_accepted', u'crema-audit__state__itemfrozen',
    u'crema-audit__state__accepted_out_of_meeting_emergency',
    u'crema-audit__state__accepted_but_modified',
    u'crema-audit__state__accepted_out_of_meeting',
    u'crema-audit__state__refused', u'crema-remun__state__accepted',
    u'crema-remun__state__validated', u'crema-remun__state__presented',
    u'crema-remun__state__delayed', u'crema-remun__state__pre_accepted',
    u'crema-remun__state__itemfrozen',
    u'crema-remun__state__accepted_out_of_meeting_emergency',
    u'crema-remun__state__accepted_but_modified',
    u'crema-remun__state__accepted_out_of_meeting',
    u'crema-remun__state__refused', u'crema-ag__state__accepted',
    u'crema-ag__state__validated', u'crema-ag__state__presented',
    u'crema-ag__state__delayed', u'crema-ag__state__pre_accepted',
    u'crema-ag__state__itemfrozen',
    u'crema-ag__state__accepted_out_of_meeting_emergency',
    u'crema-ag__state__accepted_but_modified',
    u'crema-ag__state__accepted_out_of_meeting', u'crema-ag__state__refused',
    u'idefin-ca__state__accepted', u'idefin-ca__state__validated',
    u'idefin-ca__state__presented', u'idefin-ca__state__delayed',
    u'idefin-ca__state__pre_accepted', u'idefin-ca__state__itemfrozen',
    u'idefin-ca__state__accepted_out_of_meeting_emergency',
    u'idefin-ca__state__accepted_but_modified',
    u'idefin-ca__state__accepted_out_of_meeting', u'idefin-ca__state__refused',
    u'idefin-audit__state__accepted', u'idefin-audit__state__validated',
    u'idefin-audit__state__presented', u'idefin-audit__state__delayed',
    u'idefin-audit__state__pre_accepted', u'idefin-audit__state__itemfrozen',
    u'idefin-audit__state__accepted_out_of_meeting_emergency',
    u'idefin-audit__state__accepted_but_modified',
    u'idefin-audit__state__accepted_out_of_meeting',
    u'idefin-audit__state__refused', u'idefin-remun__state__accepted',
    u'idefin-remun__state__validated', u'idefin-remun__state__presented',
    u'idefin-remun__state__delayed', u'idefin-remun__state__pre_accepted',
    u'idefin-remun__state__itemfrozen',
    u'idefin-remun__state__accepted_out_of_meeting_emergency',
    u'idefin-remun__state__accepted_but_modified',
    u'idefin-remun__state__accepted_out_of_meeting',
    u'idefin-remun__state__refused', u'idefin-ag__state__accepted',
    u'idefin-ag__state__validated', u'idefin-ag__state__presented',
    u'idefin-ag__state__delayed', u'idefin-ag__state__pre_accepted',
    u'idefin-ag__state__itemfrozen',
    u'idefin-ag__state__accepted_out_of_meeting_emergency',
    u'idefin-ag__state__accepted_but_modified',
    u'idefin-ag__state__accepted_out_of_meeting', u'idefin-ag__state__refused']
fin_org = OrgDescriptor('finances-et-comptabilite', u'Finances et Comptabilité', u'FIN')
fin_org.item_advice_states = jur_org.item_advice_states
fin_org.item_advice_edit_states = jur_org.item_advice_edit_states
fin_org.item_advice_view_states = jur_org.item_advice_view_states
log_org = OrgDescriptor('logistique', u'Logistique & Recyparcs', u'Logistic & Recyparc')
logcs_org = OrgDescriptor('logistic-recyparcs-chef-de-serivce',
                          u'Logistique & Recyparcs (Chef de service)',
                          u'Logistic & recyparc (chef)')
rhc_org = OrgDescriptor('ressources-humaines-confidentiel', u'Ressources Humaines (Confidentiel)', u'RHC')
sr_org = OrgDescriptor('services-generaux', u'Services Généraux', u'SG')
info_org = OrgDescriptor('informatique', u'Informatique', u'INFO')
de_org = OrgDescriptor('developpement-economique', u'Développement Économiqe', u'DE')
ce_org = OrgDescriptor('coaching-entreprises', u'Coaching Entreprises', u'CE')
cecs_org = OrgDescriptor('coaching-entreprises-chef-de-service', u'Coaching Entreprises (Chef de service)', u'CECS')
ai_org = OrgDescriptor('attraction-investisseurs', u'Parcs d\'activités et Attraction d\'entreprises', u'AI')
ess_org = OrgDescriptor('essaimage', u'Essaimage', u'Essaimage')
is_org = OrgDescriptor('intelligence-strategique', u'Intelligence Stratégique', u'IS')
env_org = OrgDescriptor('environnement', u'Environnement', u'ENV')
fact_org = OrgDescriptor('facturation', u'Facturation', u'FACT')
sn_org = OrgDescriptor('strategie-numerique', u'Stratégie numérique', u'Stratégie numérique')
appit_org = OrgDescriptor('applications-it', u'Applications IT', u'ApplicationsIT')
pe_org = OrgDescriptor('programmes-europeens-territoriaux',
                       u'Programmes Européens Territoriaux ',
                       u'Programmes Européens Territoriaux ')
dt_org = OrgDescriptor('developpement-territorial', u'Développement Territorial', u'DT')
mo_org = OrgDescriptor('maitrise-douvrages', u'Maitrise d\'ouvrages', u'MO')
mocs_org = OrgDescriptor('maitrise-douvrage-chef-de-service',
                         u'Maitrise d\'ouvrages (Chef de service)',
                         u'Maîtrise (chef)')
ti_org = OrgDescriptor('traitement-industriel',
                       u'Traitement industriel & études de projets',
                       u'Traitement ind et étude projets')
tics_org = OrgDescriptor('traitement-industriel-etudes-de-projets-chef-de-service',
                         u'Traitement industriel & études de projets (Chef de service)',
                         u'')
infrait_org = OrgDescriptor('infrastructure-it', u'Infrastructure IT', u'InfrastructureIT')
infra_org = OrgDescriptor('infrastructure', u'Infrastructure', u'INFRA')
amt_org = OrgDescriptor('amenagement-du-territoire', u'Aménagement du territoire', u'AMT')
ac_org = OrgDescriptor('actions-collectives', u'Actions collectives', u'Actions collectives')
incub_org = OrgDescriptor('incubateur-etudiants', u'Incubateur étudiants', u'Incubateur étudiants')
ca_restrictedpowerobservers = PloneGroupDescriptor(
    'meeting-config-ca_restrictedpowerobservers',
    'meeting-config-ca_restrictedpowerobservers',
    [])
assembly_member.ploneGroups = [ca_restrictedpowerobservers]

dg_org.advisers.append(rde)
dg_org.creators.append(rde)
dg_org.reviewers.append(rde)

sg_org.advisers.append(ogr)
sg_org.creators += [ito, jca, ogr, str_user]
sg_org.reviewers.append(ogr)
sgcs_org.advisers.append(ogr)

com_org.advisers += [ibe, sma]
com_org.creators += [ibe, sma]
com_org.reviewers += [ibe, sma]

jur_org.advisers += [ajo, mdu]
jur_org.creators += [ajo, mdu]
jur_org.reviewers += [ajo]

fin_org.advisers += [ajo, fma, mdu]
fin_org.creators += [ajo, fma, mdu]
fin_org.reviewers += [ajo, fma]

info_org.advisers += [gqu, jyp, mdr, pli, sbr, the]
info_org.creators += [gqu, jyp, mdr, pli, sbr, the]
info_org.reviewers += [mdr]

ce_org.advisers += [cbo, dlo, dma, dde, ebe, jpo, lgo, mdh, nvg, qox]
ce_org.creators += [cbo, dlo, dma, dde, ebe, jpo, lgo, mdh, nvg, qox]
ce_org.reviewers += [lgo]
cecs_org.advisers += [dma]

rhc_org.advisers = [isa]
rhc_org.creators = [isa]
rhc_org.reviewers = [isa]

# Meeting configurations -------------------------------------------------------
# BEP - CA
bepca = deepcopy(simple_import_data.simpleMeeting)
bepca.id = 'bep-ca'
bepca.title = "Conseil d'Administration"
bepca.folderTitle = "Conseil d'Administration"
bepca.shortName = 'BepCA'
bepca.configGroup = 'bep'
bepca.podTemplates = templates
bepca.addContacts = True

# BEP - Audit
bepaudit = deepcopy(simple_import_data.simpleMeeting)
bepaudit.id = 'bep-audit'
bepaudit.title = "Comité d'Audit"
bepaudit.shortName = 'BepAudit'
bepaudit.configGroup = 'bep'
bepaudit.folderTitle = "Comité d'Audit"
bepaudit.podTemplates = reuse_templates

# BEP - Rémunération
bepremun = deepcopy(simple_import_data.simpleMeeting)
bepremun.id = 'bep-remun'
bepremun.title = "Comité de Rémunération"
bepremun.shortName = 'BepRemun'
bepremun.configGroup = 'bep'
bepremun.folderTitle = "Comité de Rémunération"
bepremun.podTemplates = reuse_templates

# BEP - AG
bepag = deepcopy(simple_import_data.simpleMeeting)
bepag.id = 'bep-ag'
bepag.title = "Assemblée Générale"
bepag.shortName = 'BepAG'
bepag.configGroup = 'bep'
bepag.folderTitle = "Assemblée Générale"
bepag.podTemplates = reuse_templates

# EXPA - CA
expaca = deepcopy(simple_import_data.simpleMeeting)
expaca.id = 'expa-ca'
expaca.title = "Conseil d'Administration"
expaca.folderTitle = "Conseil d'Administration"
expaca.shortName = 'ExpaCA'
expaca.configGroup = 'expa'
expaca.podTemplates = reuse_templates

# EXPA - Audit
expaaudit = deepcopy(simple_import_data.simpleMeeting)
expaaudit.id = 'expa-audit'
expaaudit.title = "Comité d'Audit"
expaaudit.shortName = 'ExpaAudit'
expaaudit.configGroup = 'expa'
expaaudit.folderTitle = "Comité d'Audit"
expaaudit.podTemplates = reuse_templates

# EXPA - Rémunération
exparemun = deepcopy(simple_import_data.simpleMeeting)
exparemun.id = 'expa-remun'
exparemun.title = "Comité de Rémunération"
exparemun.shortName = 'ExpaRemun'
exparemun.configGroup = 'expa'
exparemun.folderTitle = "Comité de Rémunération"
exparemun.podTemplates = reuse_templates

# EXPA - AG
expaag = deepcopy(simple_import_data.simpleMeeting)
expaag.id = 'expa-ag'
expaag.title = "Assemblée Générale"
expaag.shortName = 'ExpaAG'
expaag.configGroup = 'expa'
expaag.folderTitle = "Assemblée Générale"
expaag.podTemplates = reuse_templates

# ENVIRO - CA
enviroca = deepcopy(simple_import_data.simpleMeeting)
enviroca.id = 'enviro-ca'
enviroca.title = "Conseil d'Administration"
enviroca.folderTitle = "Conseil d'Administration"
enviroca.shortName = 'EnviroCA'
enviroca.configGroup = 'enviro'
enviroca.podTemplates = reuse_templates

# ENVIRO - Audit
enviroaudit = deepcopy(simple_import_data.simpleMeeting)
enviroaudit.id = 'enviro-audit'
enviroaudit.title = "Comité d'Audit"
enviroaudit.shortName = 'EnviroAudit'
enviroaudit.configGroup = 'enviro'
enviroaudit.folderTitle = "Comité d'Audit"
enviroaudit.podTemplates = reuse_templates

# ENVIRO - Rémunération
enviroremun = deepcopy(simple_import_data.simpleMeeting)
enviroremun.id = 'enviro-remun'
enviroremun.title = "Comité de Rémunération"
enviroremun.shortName = 'EnviroRemun'
enviroremun.configGroup = 'enviro'
enviroremun.folderTitle = "Comité de Rémunération"
enviroremun.podTemplates = reuse_templates

# ENVIRO - AG
enviroag = deepcopy(simple_import_data.simpleMeeting)
enviroag.id = 'enviro-ag'
enviroag.title = "Assemblée Générale"
enviroag.shortName = 'EnviroAG'
enviroag.configGroup = 'enviro'
enviroag.folderTitle = "Assemblée Générale"
enviroag.podTemplates = reuse_templates

# CREMA - CA
cremaca = deepcopy(simple_import_data.simpleMeeting)
cremaca.id = 'crema-ca'
cremaca.title = "Conseil d'Administration"
cremaca.folderTitle = "Conseil d'Administration"
cremaca.shortName = 'CremaCA'
cremaca.configGroup = 'crema'
cremaca.podTemplates = reuse_templates

# CREMA - Audit
cremaaudit = deepcopy(simple_import_data.simpleMeeting)
cremaaudit.id = 'crema-audit'
cremaaudit.title = "Comité d'Audit"
cremaaudit.shortName = 'CremaAudit'
cremaaudit.configGroup = 'crema'
cremaaudit.folderTitle = "Comité d'Audit"
cremaaudit.podTemplates = reuse_templates

# CREMA - Rémunération
cremaremun = deepcopy(simple_import_data.simpleMeeting)
cremaremun.id = 'crema-remun'
cremaremun.title = "Comité de Rémunération"
cremaremun.shortName = 'CremaRemun'
cremaremun.configGroup = 'crema'
cremaremun.folderTitle = "Comité de Rémunération"
cremaremun.podTemplates = reuse_templates

# CREMA - AG
cremaag = deepcopy(simple_import_data.simpleMeeting)
cremaag.id = 'crema-ag'
cremaag.title = "Assemblée Générale"
cremaag.shortName = 'CremaAG'
cremaag.configGroup = 'crema'
cremaag.folderTitle = "Assemblée Générale"
cremaag.podTemplates = reuse_templates

# IDEFIN - CA
idefinca = MeetingConfigDescriptor(
    'idefin-ca', "Conseil d'Administration", "Conseil d'Administration", isDefault=False)
idefinca = deepcopy(simple_import_data.simpleMeeting)
idefinca.id = 'idefin-ca'
idefinca.title = "Conseil d'Administration"
idefinca.folderTitle = "Conseil d'Administration"
idefinca.shortName = 'IdefinCA'
idefinca.configGroup = 'idefin'
idefinca.podTemplates = reuse_templates

# IDEFIN - Audit
idefinaudit = deepcopy(simple_import_data.simpleMeeting)
idefinaudit.id = 'idefin-audit'
idefinaudit.title = "Comité d'Audit"
idefinaudit.shortName = 'IdefinAudit'
idefinaudit.configGroup = 'idefin'
idefinaudit.folderTitle = "Comité d'Audit"
idefinaudit.podTemplates = reuse_templates

# IDEFIN - Rémunération
idefinremun = deepcopy(simple_import_data.simpleMeeting)
idefinremun.id = 'idefin-remun'
idefinremun.title = "Comité de Rémunération"
idefinremun.shortName = 'IdefinRemun'
idefinremun.configGroup = 'idefin'
idefinremun.folderTitle = "Comité de Rémunération"
idefinremun.podTemplates = reuse_templates

# IDEFIN - AG
idefinag = deepcopy(simple_import_data.simpleMeeting)
idefinag.id = 'idefin-ag'
idefinag.title = "Assemblée Générale"
idefinag.shortName = 'IdefinAG'
idefinag.configGroup = 'idefin'
idefinag.folderTitle = "Assemblée Générale"
idefinag.podTemplates = reuse_templates

cfgs = (bepca, bepaudit, bepremun, bepag,
        expaca, expaaudit, exparemun, expaag,
        enviroca, enviroaudit, enviroremun, enviroag,
        cremaca, cremaaudit, cremaremun, cremaag,
        idefinca, idefinaudit, idefinremun, idefinag)

for cfg in cfgs:
    cfg.styleTemplates = [examples_fr_import_data.stylesTemplate1]
    cfg.budgetDefault = '<p>La dépense sera imputée sur le budget n°<span class="highlight-yellow"> XXX</span> ' \
        'dont le solde permet de supporter celle-ci.</p>'
    cfg.places = """Salle du Conseil\r
Salle Vivace\r
Salle Adagio\r
Extérieur\r"""

    # assembly and signatures
    cfg.assembly = ""
    cfg.signatures = ""
    cfg.certifiedSignatures = (
        {'function': 'Directeur, Secr\xc3\xa9tariat G\xc3\xa9n\xc3\xa9ral',
         'signatureNumber': '1',
         'date_from': '',
         'name': 'O. GRANVILLE',
         'held_position': '',
         'date_to': ''},
        {'function': 'Le Signataire 2 FF',
         'signatureNumber': '2',
         'date_from': '',
         'name': 'Vraiment Exemple',
         'held_position': '',
         'date_to': ''},
        {'function': 'Charg\xc3\xa9 de Mission',
         'signatureNumber': '3',
         'date_from': '',
         'name': 'S. TRIFFOY',
         'held_position': '',
         'date_to': ''},
        {'function': 'Directeur, Secr\xc3\xa9tariat G\xc3\xa9n\xc3\xa9ral',
         'signatureNumber': '4',
         'date_from': '',
         'name': 'O. GRANVILLE',
         'held_position': '',
         'date_to': ''})
    # data
    cfg.useGroupsAsCategories = False
    cfg.usedItemAttributes = (u'budgetInfos', u'emergency', u'motivation', u'toDiscuss',
                              u'notes', u'manuallyLinkedItems', u'sendToAuthority', 'copyGroups')
    cfg.usedMeetingAttributes = (u'start_date',
                                 u'end_date',
                                 u'assembly_guests',
                                 u'attendees',
                                 u'excused',
                                 u'signatories',
                                 u'replacements',
                                 u'place',
                                 u'observations')
    # AG
    if cfg.id.endswith('-ag'):
        cfg.usedMeetingAttributes = ['start_date', 'end_date', 'assembly', u'assembly_guests',
                                     'signatures', 'place', 'observations', ]
    cfg.categories = categories

    # gui
    cfg.itemColumns = (u'static_item_reference', u'Creator', u'ModificationDate', u'review_state',
                       u'getCategory', u'proposing_group_acronym', u'advices', u'meeting_date',
                       u'preferred_meeting_date', u'actions')
    cfg.meetingColumns = (u'Creator', u'CreationDate', u'review_state', u'actions')
    cfg.itemsListVisibleColumns = (u'static_item_reference', u'Creator', u'ModificationDate', u'review_state',
                                   u'getCategory', u'proposing_group_acronym', u'advices', u'actions')
    cfg.availableItemsListVisibleColumns = (u'Creator', u'ModificationDate', u'getCategory',
                                            u'proposing_group_acronym', u'advices', u'preferred_meeting_date',
                                            u'actions')
    cfg.dashboardItemsListingsFilters = (u'c4', u'c5', u'c6', u'c7', u'c8', u'c9', u'c10', u'c11',
                                         u'c13', u'c14', u'c15', u'c17', u'c18', u'c19')
    cfg.dashboardMeetingAvailableItemsFilters = (u'c4', u'c5', u'c7', u'c8', u'c11',
                                                 u'c13', u'c14', u'c17', u'c19')
    cfg.dashboardMeetingLinkedItemsFilters = (u'c4', u'c5', u'c6', u'c7', u'c8',
                                              u'c11', u'c13', u'c14', u'c17', u'c19')
    cfg.disabled_collections = [
        'searches_items/searchmyitemstakenover', 'searches_items/searchitemstoprevalidate',
        'searches_items/searchitemstoadvicewithoutdelay', 'searches_items/searchitemstoadvicewithdelay',
        'searches_items/searchitemstoadvicewithexceededdelay', 'searches_items/searchalladviseditemswithdelay',
        'searches_items/searchitemstocorrect', 'searches_items/searchitemstocorrecttovalidate',
        'searches_items/searchitemstocorrecttovalidateoffeveryreviewergroups',
        'searches_items/searchcorrecteditems',
        'searches_items/searchitemswithfinanceadvice', 'searches_items/searchitemstocontrolcompletenessof',
        'searches_items/searchadviceproposedtocontroller', 'searches_items/searchadviceproposedtoeditor',
        'searches_items/searchadviceproposedtoreviewer', 'searches_items/searchadviceproposedtomanager'
    ]
    # workflow
    cfg.workflowAdaptations = (
        u'no_publication',
        u'presented_item_back_to_proposed',  # u'return_to_proposing_group',
        u'accepted_out_of_meeting',
        u'accepted_out_of_meeting_emergency_and_duplicated',
        u'pre_accepted',
        u'accepted_but_modified',
        u'delayed',
        u'refused', )
    cfg.itemConditionsInterface = 'Products.MeetingBEP.interfaces.IMeetingItemBEPWorkflowConditions'
    cfg.itemActionsInterface = 'Products.MeetingBEP.interfaces.IMeetingItemBEPWorkflowActions'
    cfg.meetingConditionsInterface = 'Products.MeetingBEP.interfaces.IMeetingBEPWorkflowConditions'
    cfg.meetingActionsInterface = 'Products.MeetingBEP.interfaces.IMeetingBEPWorkflowActions'
    cfg.transitionsToConfirm = (
        u'MeetingItem.accept_but_modify', u'MeetingItem.accept_out_of_meeting_emergency',
        u'MeetingItem.accept_out_of_meeting', u'MeetingItem.pre_accept',
        u'MeetingItem.propose', u'MeetingItem.refuse', u'MeetingItem.backToItemCreated',
        u'MeetingItem.backToProposed', u'MeetingItem.backToValidatedFromAcceptedOutOfMeeting',
        u'MeetingItem.backToValidatedFromAcceptedOutOfMeetingEmergency', u'MeetingItem.delay',
        u'MeetingItem.backToValidated', u'MeetingItem.validate')
    cfg.itemDecidedStates = (
        u'accepted', u'accepted_but_modified', u'accepted_out_of_meeting',
        u'accepted_out_of_meeting_emergency', u'pre_accepted', u'refused', u'delayed')
    cfg.itemPositiveDecidedStates = (
        u'accepted', u'accepted_but_modified', u'accepted_out_of_meeting',
        u'accepted_out_of_meeting_emergency', u'pre_accepted')
    cfg.onTransitionFieldTransforms = (
        {'transition': 'validate',
         'field_name': 'MeetingItem.decision',
         'tal_expression': 'python: here.adapted().adaptDecisionClonedItem()'},)
    cfg.onMeetingTransitionItemTransitionToTrigger = (
        {'meeting_transition': 'freeze', 'item_transition': 'itemfreeze'},
        {'meeting_transition': 'decide', 'item_transition': 'itemfreeze'},
        {'meeting_transition': 'close', 'item_transition': 'itemfreeze'},
        {'meeting_transition': 'close', 'item_transition': 'accept'})
    # advices and access
    cfg.usedAdviceTypes = (u'positive', u'positive_with_remarks', u'negative', u'nil')
    cfg.enableAdviceConfidentiality = True
    cfg.adviceConfidentialityDefault = True
    cfg.itemPowerObserversStates = (u'accepted', u'accepted_but_modified', u'pre_accepted',
                                    u'itemfrozen', u'refused', u'delayed')
    cfg.meetingPowerObserversStates = (u'closed', u'decided', u'frozen')
    cfg.itemRestrictedPowerObserversStates = (u'accepted', u'accepted_but_modified', u'pre_accepted',
                                              u'itemfrozen', u'refused', u'delayed')
    cfg.meetingRestrictedPowerObserversStates = (u'closed', u'decided', u'frozen')
    cfg.adviceConfidentialFor = ('restrictedpowerobservers', )
    cfg.hideHistoryTo = ('MeetingItem.restrictedpowerobservers', )
    cfg.itemAdviceStates = ('proposed',)
    cfg.itemAdviceEditStates = ('proposed',)
    cfg.itemAdviceViewStates = (u'accepted', u'accepted_but_modified', u'accepted_out_of_meeting',
                                u'accepted_out_of_meeting_emergency', u'pre_accepted', u'itemfrozen',
                                u'proposed', u'presented', u'refused', u'delayed', u'validated')
    cfg.customAdvisers = (
        {'delay_label': '',
         'for_item_created_until': '',
         'available_on': '',
         'delay': '',
         'gives_auto_advice_on_help_message': '',
         'gives_auto_advice_on': 'python: True',
         'org': 'service-juridique',
         'delay_left_alert': '',
         'is_linked_to_previous_row': '0',
         'for_item_created_from': '2018/01/01',
         'row_id': '2018-12-14.3789235136'},
        {'delay_label': '',
         'for_item_created_until': '',
         'available_on': '',
         'delay': '',
         'gives_auto_advice_on_help_message': '',
         'gives_auto_advice_on': 'python: True',
         'org': 'finances-et-comptabilite',
         'delay_left_alert': '',
         'is_linked_to_previous_row': '0',
         'for_item_created_from': '2018/01/01',
         'row_id': 'row_id_2'},
        {'delay_label': '',
         'for_item_created_until': '',
         'available_on': '',
         'delay': '',
         'gives_auto_advice_on_help_message': '',
         'gives_auto_advice_on': "python: item.getProposingGroup() == pm_utils.org_id_to_uid('coaching-entreprises')",
         'org': 'coaching-entreprises-chef-de-service',
         'delay_left_alert': '',
         'is_linked_to_previous_row': '0',
         'for_item_created_from': '2018/08/01',
         'row_id': 'row_id_1'},
        {'delay_label': '',
         'for_item_created_until': '',
         'available_on': '',
         'delay': '',
         'gives_auto_advice_on_help_message': '',
         'gives_auto_advice_on': "python: item.getProposingGroup() == pm_utils.org_id_to_uid('communication')",
         'org': 'communication-web-chef-de-service',
         'delay_left_alert': '',
         'is_linked_to_previous_row': '0',
         'for_item_created_from': '2018/12/09',
         'row_id': '2018-12-09.4064779048'},
        {'delay_label': '',
         'for_item_created_until': '',
         'available_on': '',
         'delay': '',
         'gives_auto_advice_on_help_message': '',
         'gives_auto_advice_on': "python: item.getProposingGroup() == pm_utils.org_id_to_uid('logistique')",
         'org': 'logistic-recyparcs-chef-de-serivce',
         'delay_left_alert': '',
         'is_linked_to_previous_row': '0',
         'for_item_created_from': '2018/12/09',
         'row_id': '2018-12-09.4064775388'},
        {'delay_label': '',
         'for_item_created_until': '',
         'available_on': '',
         'delay': '',
         'gives_auto_advice_on_help_message': '',
         'gives_auto_advice_on': "python: item.getProposingGroup() == pm_utils.org_id_to_uid('maitrise-douvrages')",
         'org': 'maitrise-douvrage-chef-de-service',
         'delay_left_alert': '',
         'is_linked_to_previous_row': '0',
         'for_item_created_from': '2018/12/09',
         'row_id': '2018-12-09.4064772101'},
        {'delay_label': '',
         'for_item_created_until': '',
         'available_on': '',
         'delay': '',
         'gives_auto_advice_on_help_message': '',
         'gives_auto_advice_on': "python: item.getProposingGroup() == pm_utils.org_id_to_uid('secretariat')",
         'org': 'secretariat-general-chef-de-service',
         'delay_left_alert': '',
         'is_linked_to_previous_row': '0',
         'for_item_created_from': '2018/12/09',
         'row_id': '2018-12-09.4064780584'},
        {'delay_label': '',
         'for_item_created_until': '',
         'available_on': '',
         'delay': '',
         'gives_auto_advice_on_help_message': '',
         'gives_auto_advice_on': "python: item.getProposingGroup() == pm_utils.org_id_to_uid('traitement-industriel')",
         'org': 'traitement-industriel-etudes-de-projets-chef-de-service',
         'delay_left_alert': '',
         'is_linked_to_previous_row': '0',
         'for_item_created_from': '2018/12/09',
         'row_id': '2018-12-09.4064787347'})
    cfg.selectableCopyGroups = (
        u'dirgen_reviewers',
        u'secretariat_reviewers',
        u'communication_reviewers',
        u'service-juridique_reviewers',
        u'finances-et-comptabilite_reviewers',
        u'ressources-humaines-confidentiel_reviewers',
        u'services-generaux_reviewers',
        u'informatique_reviewers',
        u'developpement-economique_reviewers',
        u'coaching-entreprises_reviewers',
        u'attraction-investisseurs_reviewers',
        u'essaimage_reviewers',
        u'intelligence-strategique_reviewers',
        u'environnement_reviewers',
        u'facturation_reviewers',
        u'strategie-numerique_reviewers',
        u'applications-it_reviewers',
        u'programmes-europeens-territoriaux_reviewers',
        u'bureau-detudes_reviewers',
        u'developpement-territorial_reviewers',
        u'maitrise-douvrages_reviewers',
        u'infrastructure-it_reviewers',
        u'infrastructure_reviewers',
        u'amenagement-du-territoire_reviewers',
        u'actions-collectives_reviewers',
        u'incubateur-etudiants_reviewers',
        u'traitement-industriel_reviewers')
    cfg.itemCopyGroupsStates = (
        u'accepted', u'accepted_but_modified', u'accepted_out_of_meeting',
        u'accepted_out_of_meeting_emergency', u'pre_accepted',
        u'itemfrozen', u'refused', u'delayed')
    cfg.powerAdvisersGroups = (u'dirgen', )

data = PloneMeetingConfiguration(
    meetingFolderTitle='Mes séances',
    meetingConfigs=cfgs,
    orgs=[
        dg_org, sg_org, sgcs_org, com_org, comcs_org, jur_org, fin_org, log_org, logcs_org, rhc_org, sr_org,
        info_org, de_org, ce_org, cecs_org, ai_org, ess_org, is_org, env_org, fact_org,
        sn_org, appit_org, pe_org, ti_org, tics_org, dt_org, mo_org, mocs_org, infrait_org, infra_org,
        amt_org, ac_org, incub_org])
data.configGroups = (
    {'row_id': 'bep', 'label': 'BEP'},
    {'row_id': 'expa', 'label': 'EXPA'},
    {'row_id': 'enviro', 'label': 'ENVIRO'},
    {'row_id': 'crema', 'label': 'CREMA'},
    {'row_id': 'idefin', 'label': 'IDEFIN'},
)
data.usersOutsideGroups = [assembly_member]
data.directory_position_types = [
    {'token': u'default',
     'name': u'-'},
    {'token': u'president',
     'name': u'Pr\xe9sident|Pr\xe9sidents|Pr\xe9sidente|Pr\xe9sidentes'},
    {'token': u'vice-president',
     'name': u'Vice-Pr\xe9sident|Vice-Pr\xe9sidents|Vice-Pr\xe9sidente|Vice-Pr\xe9sidentes'},
    {'token': u'admin',
     'name': u'Administrateur|Administrateurs|Administratrice|Administratrices'},
    {'token': u'dg',
     'name': u'Directeur G\xe9n\xe9ral du BEP|Directeurs G\xe9n\xe9raux du BEP|'
        u'Directrice G\xe9n\xe9rale du BEP|Directrices G\xe9n\xe9rales du BEP'},
    {'token': u'dgff',
     'name': u'Directeur G\xe9n\xe9ral du BEP f.f.|Directeurs G\xe9n\xe9raux du BEP f.f.|'
        u'Directrice G\xe9n\xe9rale du BEP f.f.|Directrices G\xe9n\xe9rales du BEP f.f.'},
    {'token': u'directeur',
     'name': u'Directeur|Directeurs|Directrice|Directrices'}]
