import React, { Component } from 'react'
import { Redirect } from 'react-router'
import PropTypes from 'prop-types'

import { connect } from 'react-redux'

import { fetchSosModel } from 'actions/actions.js'
import { fetchSectorModels } from 'actions/actions.js'
import { fetchScenarios } from 'actions/actions.js'

import { saveSosModel } from 'actions/actions.js'

import { setAppFormEdit } from 'actions/actions.js'
import { setAppFormCancel } from 'actions/actions.js'
import { setAppFormCancelDone } from 'actions/actions.js'
import { setAppFormSave } from 'actions/actions.js'
import { setAppFormSaveDone } from 'actions/actions.js'
import { setAppRedirect } from 'actions/actions.js'

import SosModelConfigForm from 'components/ConfigForm/SosModelConfigForm.js'
import { ConfirmPopup } from 'components/ConfigForm/General/Popups.js'

class SosModelConfig extends Component {
    constructor(props) {
        super(props)
        const { dispatch } = this.props

        this.openClosePopup = this.openClosePopup.bind(this)

        this.config_name = this.props.match.params.name

        this.state = {
            openClosePopup: false,
            closeForm: false
        }

        dispatch(fetchSosModel(this.config_name))
        dispatch(fetchSectorModels())
        dispatch(fetchScenarios())
    }

    componentDidUpdate() {
        const { dispatch } = this.props

        if (this.config_name != this.props.match.params.name) {
            this.config_name = this.props.match.params.name
            this.setState({closeForm: false})
            dispatch(fetchSosModel(this.config_name))
        }
    }

    openClosePopup() {
        const { dispatch } = this.props
        dispatch(setAppRedirect('/configure/sos-models'))
        
        if (this.props.app.formEdit) {
            this.setState({openClosePopup: true})
        } else {
            dispatch(setAppFormCancel())
        }
    }

    renderLoading() {
        return (
            <div className="alert alert-primary">
                Loading...
            </div>
        )
    }

    renderError(error) {
        return (
            <div>
                {            
                    Object.keys(error).map(exception => (
                        <div key={exception} className="alert alert-danger">
                            {exception}
                            {
                                error[exception].map(ex => (
                                    <div key={ex}>
                                        {ex}
                                    </div>
                                ))
                            }
                        </div>
                    ))
                }
            </div>
        )
    }

    renderSosModelConfig(sos_model, sector_models, scenarios, error) {
        const { dispatch } = this.props
        return (
            <div>
                <SosModelConfigForm 
                    sos_model={sos_model} 
                    sector_models={sector_models} 
                    scenarios={scenarios} 
                    error={error} 
                    onSave={() => dispatch(setAppFormSave())} 
                    onCancel={this.openClosePopup}
                    onEdit={() => dispatch(setAppFormEdit())}/>
                <ConfirmPopup 
                    onRequestOpen={this.state.openClosePopup}
                    onSave={() => dispatch(setAppFormSave())}
                    onConfirm={() => dispatch(setAppFormCancel())}
                    onCancel={() => this.setState({openClosePopup: false})}/>
            </div>
        )
    }

    render () {
        const {sos_model, sector_models, scenarios, error, isFetching, app} = this.props
        const { dispatch } = this.props

        if (app.formReqCancel) {
            dispatch(setAppFormCancelDone())
        }
        if (app.formReqSave) {
            this.setState({openClosePopup: false})
            dispatch(saveSosModel(this.props.sos_model))
            dispatch(setAppFormSaveDone())
        }

        if (isFetching) {
            return this.renderLoading()
        } else if (
            Object.keys(error).includes('SmifDataNotFoundError') ||
            Object.keys(error).includes('SmifValidationError')) {
            return this.renderError(error)
        } else {
            return this.renderSosModelConfig(sos_model, sector_models, scenarios, error)
        }
    }
}

SosModelConfig.propTypes = {
    app: PropTypes.object.isRequired,
    sos_model: PropTypes.object.isRequired,
    sector_models: PropTypes.array.isRequired,
    scenarios: PropTypes.array.isRequired,
    error: PropTypes.object.isRequired,
    isFetching: PropTypes.bool.isRequired,
    dispatch: PropTypes.func.isRequired,
    match: PropTypes.object.isRequired,
    history: PropTypes.object.isRequired
}

function mapStateToProps(state) {
    return {
        app: state.app,
        sos_model: state.sos_model.item,
        sector_models: state.sector_models.items,
        scenarios: state.scenarios.items,
        error: ({
            ...state.sos_model.error,
            ...state.sector_models.error,
            ...state.scenarios.error
        }),
        isFetching: (
            state.sos_model.isFetching ||
            state.sector_models.isFetching ||
            state.scenarios.isFetching
        )
    }
}

export default connect(mapStateToProps)(SosModelConfig)
