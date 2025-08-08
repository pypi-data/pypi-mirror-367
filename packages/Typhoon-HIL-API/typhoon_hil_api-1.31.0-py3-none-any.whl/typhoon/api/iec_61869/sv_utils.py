import os.path
import xml.etree.ElementTree as ET
from typhoon.api.iec_61869.exceptions import IEC61869SVValidationException

VARIANTS = ["F4000S1", "F4800S1", "F4800S2", "F5760S1", "F12800S8", "F14400S6", "F15360S8"]

def get_attrib_val(obj, attrib_name):
    try:
        return obj.attrib[attrib_name]
    except KeyError:
        return ""

def parse_scl_file(file_path):
    if os.path.isfile(file_path) is False:
        raise IEC61869SVValidationException("Provided file path does not exists.")

    scl_tree = ET.parse(file_path)
    scl_root = scl_tree.getroot()

    root_tag = scl_root.tag
    scl_prefix = root_tag[: root_tag.find("}") + 1]

    scl = {}

    ieds = scl_root.findall(scl_prefix + "IED")

    for ied in ieds:
        ied_name = get_attrib_val(ied, "name")
        scl[ied_name] = {}

        AccessPoints = ied.findall(scl_prefix + "AccessPoint")
        for AccessPoint in AccessPoints:
            AccessPoint_name = AccessPoint.attrib["name"]
            scl[ied_name][AccessPoint_name] = {}

            LDevices = AccessPoint.findall(
                scl_prefix + "Server" + "/" + scl_prefix + "LDevice"
            )

            for LDevice in LDevices:
                LDevice_name = LDevice.attrib["inst"]
                scl[ied_name][AccessPoint_name][LDevice_name] = {}

                # LNodes = LDevice.findall(
                #     scl_prefix + "LN0"
                # )

                for LNode in LDevice:
                    lnClass = get_attrib_val(LNode, "lnClass")
                    inst = get_attrib_val(LNode, "inst")
                    ln_type_id = get_attrib_val(LNode, "lnType")
                    prefix = get_attrib_val(LNode, "prefix")

                    LNode_name = lnClass

                    scl[ied_name][AccessPoint_name][LDevice_name][LNode_name] = {}
                    scl[ied_name][AccessPoint_name][LDevice_name][LNode_name]["id"] = ln_type_id

                    DataSets = LNode.findall(scl_prefix + "DataSet")

                    for DataSet in DataSets:

                        DataSet_name = get_attrib_val(DataSet, "name")
                        DataSet_desc = get_attrib_val(DataSet, "desc")

                        scl[ied_name][AccessPoint_name][LDevice_name][LNode_name][DataSet_name] = {}
                        scl[ied_name][AccessPoint_name][LDevice_name][LNode_name][DataSet_name]["desc"] = DataSet_desc

                        FCDAs = DataSet.findall(scl_prefix + "FCDA")

                        scl[ied_name][AccessPoint_name][LDevice_name][LNode_name][DataSet_name]["FCDAs"] = []

                        for FCDA in FCDAs:
                            ldInst = get_attrib_val(FCDA, "ldInst")
                            prefix = get_attrib_val(FCDA, "prefix")
                            lnClass = get_attrib_val(FCDA, "lnClass")
                            lnInst = get_attrib_val(FCDA, "lnInst")
                            doName = get_attrib_val(FCDA, "doName")
                            daName = get_attrib_val(FCDA, "daName")
                            fc = get_attrib_val(FCDA, "fc")

                            FCDA_dict = {}

                            FCDA_dict["ldInst"] = ldInst
                            FCDA_dict["prefix"] = prefix
                            FCDA_dict["lnClass"] = lnClass
                            FCDA_dict["lnInst"] = lnInst
                            FCDA_dict["doName"] = doName
                            FCDA_dict["daName"] = daName
                            FCDA_dict["fc"] = fc

                            scl[ied_name][AccessPoint_name][LDevice_name][LNode_name][DataSet_name]["FCDAs"].append(FCDA_dict)


                    SampledValueControls = LNode.findall(scl_prefix + "SampledValueControl")

                    scl[ied_name][AccessPoint_name][LDevice_name][LNode_name]["SampledValueControl"] = []

                    for SampledValueControl in SampledValueControls:
                        datSet = get_attrib_val(SampledValueControl, "datSet")
                        confRev = get_attrib_val(SampledValueControl, "confRev")
                        smvID = get_attrib_val(SampledValueControl, "smvID")
                        multicast = get_attrib_val(SampledValueControl, "multicast")
                        smpRate = get_attrib_val(SampledValueControl, "smpRate")
                        nofASDU = get_attrib_val(SampledValueControl, "nofASDU")
                        smpMod = get_attrib_val(SampledValueControl, "smpMod")
                        svc_name = get_attrib_val(SampledValueControl, "name")

                        dataSet_dict = {}

                        dataSet_dict["datSet"] = datSet
                        dataSet_dict["confRev"] = confRev
                        dataSet_dict["smvID"] = smvID
                        dataSet_dict["multicast"] = multicast
                        dataSet_dict["smpRate"] = smpRate
                        dataSet_dict["nofASDU"] = nofASDU
                        dataSet_dict["smpMod"] = smpMod
                        dataSet_dict["svc_name"] = svc_name

                        scl[ied_name][AccessPoint_name][LDevice_name][LNode_name]["SampledValueControl"].append(dataSet_dict)

    return scl


def filter_scv(scl):
    """
    This function will filter the parsed SCL structure and return only the items containing SampledValueControl block.
    """
    filtered_scl = {}

    for ied in scl:
        for ap in scl[ied]:
            for ld in scl[ied][ap]:
                for ln in scl[ied][ap][ld]:
                    ln_data = scl[ied][ap][ld][ln]
                    if ln_data.get("SampledValueControl"):
                        filtered_scl.setdefault(ied, {}).setdefault(ap, {}).setdefault(ld, {})[ln] = ln_data

    return filtered_scl


def save_scl_configuration(mdl, item_handle, configuration):
    """
    This function will save provided configuration.
    If this change needs to be permanent, model.save() must be called after the call to this function.

    'configuration' : a dictionary containing following keys:
        'scl', 'ied_name', 'access_point', 'l_device', 'svc', 'svc_index', 'file_path'
    """
    
    mask_handle = mdl.get_mask(item_handle)

    try:
        mdl.set_property_value(mdl.prop(mask_handle, "saved_scl"), configuration["scl"])
    except KeyError:
        raise IEC61869SVValidationException("Error while saving configuration. No 'scl' key in the provided dictionary.")

    try:
        mdl.set_property_value(mdl.prop(mask_handle, "saved_ied"), configuration["ied_name"])
    except KeyError:
        raise IEC61869SVValidationException("Error while saving configuration. No 'ied_name' key in the provided dictionary.")

    try:
        mdl.set_property_value(mdl.prop(mask_handle, "saved_access_point"), configuration["access_point"])
    except KeyError:
        raise IEC61869SVValidationException("Error while saving configuration. No 'access_point' key in the provided dictionary.")

    try:
        mdl.set_property_value(mdl.prop(mask_handle, "saved_l_device"), configuration["l_device"])
    except KeyError:
        raise IEC61869SVValidationException("Error while saving configuration. No 'l_device' key in the provided dictionary.")

    try:
        mdl.set_property_value(mdl.prop(mask_handle, "saved_svc"), configuration["svc"])
    except KeyError:
        raise IEC61869SVValidationException("Error while saving configuration. No 'svc' key in the provided dictionary.")

    try:
        mdl.set_property_value(mdl.prop(mask_handle, "saved_svc_index"), configuration["svc_index"])
    except KeyError:
        raise IEC61869SVValidationException("Error while saving configuration. No 'svc_index' key in the provided dictionary.")

    try:
        mdl.set_property_value(mdl.prop(mask_handle, "saved_file_path"), configuration["file_path"])
    except KeyError:
        raise IEC61869SVValidationException("Error while saving configuration. No 'file_path' key in the provided dictionary.")


def set_configuration(mdl, item_handle, configuration, datasets, save_dict):
    """
    Set the provided configuration to the provided item in the model.

    'configuration' : dictionary containing following keys:
        'confRev', 'smvID', 'smpMod', 'smpRate', 'nofASDU', 'datSet'

    'datasets' : this can be either an item of a dictionary or a dictionary.
        If it's an item, it must be the handle of the dataSet item which is called the same as
        the value of configuration["datSet"].
        If it's a dictionary, function will search for configuration["datSet"] key in that dictionary.

    'save_dict' : this is a dictionary containing following keys:
        'scl', 'ied_name', 'access_point', 'l_device', 'svc', 'svc_index', 'file_path'

    If successful it will return a dictionary with keys: 'confRev', 'smvID', 'variant', 'i_count', 'v_count'
    """

    try:
        confRev = configuration["confRev"]
    except KeyError:
        # If there is no attribute in the configuration, skip that attribute
        confRev = ""


    try:
        smvID = configuration["smvID"]
    except KeyError:
        smvID = ""


    try:
        smpMod = configuration["smpMod"]
        if smpMod != "SmpPerSec":
            raise IEC61869SVValidationException("Only 'SmpPerSec' value for 'smpRate' is supported on IEC 61869 SV components.")

    except KeyError:
        raise IEC61869SVValidationException("No 'smpMod' attribute defined. Only 'SmpPerSec' value for 'smpRate' is supported on IEC 61869 SV components.")


    try:
        smpRate = configuration["smpRate"]
    except KeyError:
        smpRate = ""

    try:
        nofASDU = configuration["nofASDU"]
    except KeyError:
        nofASDU = ""

    variant = "F" + str(smpRate) + "S" + str(nofASDU)
    if variant not in VARIANTS:
        raise IEC61869SVValidationException(f"Variant {variant} not supported by IEC 61869 SV Publisher.")


    try:
        datSet = configuration["datSet"]
    except KeyError:
        datSet = ""


    if datasets is None or datSet == "":
        raise IEC61869SVValidationException("Non valid dataSet provided.")

    elif len(datasets) == 1:
        # user provided a dataset, check if the name matches the one in the SampledValueControl block
        if datSet == datasets[0]:
            i_count, v_count = _get_count_in_dataset(datasets[0])
        else:
            raise IEC61869SVValidationException("Non valid dataSet provided.")

    else:
        found_dataset = None
        for ds in datasets.keys():
            if ds == datSet:
                found_dataset = datasets[ds]
                break

        if found_dataset:
            i_count, v_count = _get_count_in_dataset(found_dataset)
        else:
            raise IEC61869SVValidationException("Non valid dataSet provided.")

    # Set components properties
    mask_handle = mdl.get_mask(item_handle)

    mdl.set_property_value(mdl.prop(mask_handle, "confRev"), confRev)
    mdl.set_property_value(mdl.prop(mask_handle, "svID"), smvID)
    mdl.set_property_value(mdl.prop(mask_handle, "variant"), variant)
    mdl.set_property_value(mdl.prop(mask_handle, "i_count"), i_count)
    mdl.set_property_value(mdl.prop(mask_handle, "v_count"), v_count)

    configured_values = {
        "confRev": confRev,
        "svID": smvID,
        "variant": variant,
        "i_count": i_count,
        "v_count": v_count,
    }

    save_scl_configuration(mdl, item_handle, save_dict)

    return configured_values


def parse_file(file_path):
    """
    This function loads an SCL file located on the provided path, parses it, filters it and returns a dictionary.

    file_path must be an absolute path.
    """

    if os.path.isabs(file_path) is False:
        raise IEC61869SVValidationException(f"Provided file path {file_path} is not an absolute path.")

    scl = parse_scl_file(file_path)
    filtered_scl = filter_scv(scl)

    return filtered_scl


def get_IEDs(scl):
    return list(scl.keys())


def get_AccessPoints(scl):
    return list(scl.keys())


def get_LDevices(scl):
    return list(scl.keys())


def get_LNodes(scl):
    return list(scl.keys())


def get_SampledValueControls(scl):
    return list(scl["SampledValueControl"])


def get_DataSets(scl):
    return {key: value for key, value in scl.items() if key != "SampledValueControl"}


def _get_count_in_dataset(datSet):
    i_count = 0
    v_count = 0

    try:
        FCDAs = datSet["FCDAs"]
    except KeyError:
        raise IEC61869SVValidationException("Non valid dataSet provided.")

    for instance in FCDAs:
        doName = str(instance["doName"])
        if doName.startswith("AmpSv") and instance["daName"] != "q":
            i_count += 1

        if doName.startswith("VolSv") and instance["daName"] != "q":
            v_count += 1

    return i_count, v_count

