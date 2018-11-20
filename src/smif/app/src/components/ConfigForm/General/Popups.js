import React from 'react'
import PropTypes from 'prop-types'
import Popup from 'components/ConfigForm/General/Popup'
import { SaveButton, DangerButton, CancelButton } from 'components/ConfigForm/General/Buttons'

const ConfirmPopup = (props) => (
    <div>
        <Popup name='bla' onRequestOpen={props.onRequestOpen}>
            <div>
                This form has pending changes. Are you sure you would like to leave without saving?
            </div>
            <br/>
            <div>
                <DangerButton value="Discard" onClick={props.onConfirm} />
                <CancelButton value="Keep Editing" onClick={props.onCancel}/>
                <SaveButton value="Save" onClick={props.onSave} />
            </div>
        </Popup>
    </div>
)

ConfirmPopup.propTypes = {
    onRequestOpen: PropTypes.bool,
    onSave: PropTypes.func,
    onConfirm: PropTypes.func,
    onCancel: PropTypes.func
}

export {
    ConfirmPopup
} 