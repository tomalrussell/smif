import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { connect } from 'react-redux'
import { Redirect } from 'react-router'
import { NavLink, Route } from 'react-router-dom'
import { fetchModelRuns, fetchSosModels, fetchSectorModels, fetchScenarios } from 'actions/actions.js'

import { setAppFormCancel } from 'actions/actions.js'
import { setAppFormSave } from 'actions/actions.js'
import { setAppRedirect } from 'actions/actions.js'

import { FaHome, FaTasks, FaSliders, FaSitemap, FaCode, FaBarChart } from 'react-icons/lib/fa'
import { Badge } from 'reactstrap'

import { ConfirmPopup } from 'components/ConfigForm/General/Popups.js'
import Footer from 'containers/Footer'

class Nav extends Component {
    constructor(props) {
        super(props)
        this.init = true

        this.navigate = this.navigate.bind(this)
        this.state = {
            openClosePopup: false,
        }
    }

    componentDidMount() {
        const { dispatch } = this.props

        dispatch(fetchModelRuns())
        dispatch(fetchSosModels())
        dispatch(fetchSectorModels())
        dispatch(fetchScenarios())
    }

    navigate(to) {
        const { dispatch } = this.props
        dispatch(setAppRedirect(to))

        if (this.props.app.formEdit) {
            this.setState({openClosePopup: true})
        } else {
            const { dispatch } = this.props
            dispatch(setAppFormCancel())
        }
    }

    renderLoading() {
        return (
            <nav className="col-12 col-md-3 col-xl-2 bg-light sidebar">
                <ul className="nav flex-column">
                    <li className="nav-item">
                        <NavLink exact className="nav-link" to="/">
                            <FaHome size={20}/>
                            Home
                        </NavLink>
                    </li>
                </ul>
                <div className="alert alert-primary">
                    Loading...
                </div>
            </nav>
        )
    }

    renderError() {
        return (
            <nav className="col-12 col-md-3 col-xl-2 bg-light sidebar">
                <ul className="nav flex-column">
                    <li className="nav-item">
                        <NavLink exact className="nav-link" to="/">
                            <FaHome size={20}/>
                            Home
                        </NavLink>
                    </li>
                </ul>
                <div className="alert alert-danger">
                    Error
                </div>
            </nav>
        )
    }

    renderNav(model_runs, sos_models, sector_models, scenarios) {
        var job_status = ['unstarted', 'running', 'stopped', 'done', 'failed']
        const pathname = this.props.location.pathname
        const { dispatch } = this.props

        return (
            <nav className="col-12 col-md-3 col-xl-2 bg-light sidebar">
                <ul className="nav flex-column">
                    <li className="nav-item">
                        <div className="nav-link" onClick={() => this.navigate('/')}>
                            <FaHome size={20}/>
                            Home
                        </div>
                    </li>
                </ul>

                <h6 className="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
                    <span>Simulation</span>
                </h6>
                <ul className="nav flex-column mb-2">

                    <li className="nav-item">
                        <div className="nav-link" onClick={() => this.navigate('/jobs/')}>
                            <FaTasks size={20}/>
                                Jobs
                            <Badge color="secondary">{model_runs.length}</Badge>
                        </div>
                        <Route path="/jobs/" render={() =>
                            <ul className="nav flex-column">
                                {job_status.map(status =>
                                    <li key={'nav_' + status} className="nav-item">
                                        <div 
                                            className={
                                                pathname == '/jobs/status=' + status ? 
                                                    'nav-link active' : 'nav-link'
                                            }
                                            onClick={() => this.navigate('/jobs/status=' + status)}>
                                            {status}
                                        </div>
                                    </li>
                                )}
                            </ul>
                        }/>
                    </li>

                    <li className="nav-item">
                        <div className="nav-link" onClick={() => this.navigate('/configure/model-runs')}>
                            <FaSliders size={20}/>
                                Model Runs
                            <Badge color="secondary">{model_runs.length}</Badge>
                        </div>
                        <Route path="/configure/model-runs/" render={() =>
                            <ul className="nav flex-column">
                                {model_runs.map(model_run =>
                                    <li key={'nav_modelrun_' + model_run.name} className="nav-item">
                                        <div
                                            className={
                                                pathname == '/configure/model-runs/' + model_run.name ? 
                                                    'nav-link active' : 'nav-link'
                                            }
                                            key={'nav_' + model_run.name}
                                            onClick={() => this.navigate('/configure/model-runs/' + model_run.name)}>
                                            {model_run.name}
                                        </div>
                                    </li>
                                )}
                            </ul>
                        }/>
                    </li>
                </ul>

                <h6 className="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
                    <span>Configuration</span>
                </h6>

                <ul className="nav flex-column mb-2">
                    <li className="nav-item">
                        <div className="nav-link" onClick={() => this.navigate('/configure/sos-models')}>
                            <FaSitemap size={20}/>
                                System-of-Systems Models
                            <Badge color="secondary">{sos_models.length}</Badge>
                        </div>
                        <Route path="/configure/sos-models/" render={() =>
                            <ul className="nav flex-column">
                                {sos_models.map(sos_model =>
                                    <li key={'nav_sosmodel_' + sos_model.name} className="nav-item">
                                        <div
                                            className={
                                                pathname == '/configure/sos-models/' + sos_model.name ? 
                                                    'nav-link active' : 'nav-link'
                                            }
                                            key={'nav_' + sos_model.name}
                                            onClick={() => this.navigate('/configure/sos-models/' + sos_model.name)}>
                                            {sos_model.name}
                                        </div>
                                    </li>
                                )}
                            </ul>
                        }/>

                        <div className="nav-link" onClick={() => this.navigate('/configure/sector-models')}>
                            <FaCode size={20}/>
                                Model Wrappers
                            <Badge color="secondary">{sector_models.length}</Badge>
                        </div>
                        <Route path="/configure/sector-models/" render={() =>
                            <ul className="nav flex-column">
                                {sector_models.map(sector_model =>
                                    <li key={'nav_sectormodel_' + sector_model.name} className="nav-item">
                                        <div
                                            className={
                                                pathname == '/configure/sector-models/' + sector_model.name ? 
                                                    'nav-link active' : 'nav-link'
                                            }
                                            key={'nav_' + sector_model.name}
                                            onClick={() => this.navigate('/configure/sector-models/' + sector_model.name)}>
                                            {sector_model.name}
                                        </div>
                                    </li>
                                )}
                            </ul>
                        }/>
                    </li>

                    <li className="nav-item">
                        <div className="nav-link" onClick={() => this.navigate('/configure/scenarios')}>
                            <FaBarChart size={20}/>
                                Scenarios
                            <Badge color="secondary">{scenarios.length}</Badge>
                        </div>
                        <Route path="/configure/scenarios/" render={() =>
                            <ul className="nav flex-column">
                                {scenarios.map(scenario =>
                                    <li key={'nav_scenario_' + scenario.name} className="nav-item">
                                        <div
                                            className={
                                                pathname == '/configure/scenarios/' + scenario.name ? 
                                                    'nav-link active' : 'nav-link'
                                            }
                                            key={'nav_' + scenario.name}
                                            onClick={() => this.navigate('/configure/scenarios/' + scenario.name)}>
                                            {scenario.name}
                                        </div>
                                    </li>
                                )}
                            </ul>
                        }/>
                    </li>
                </ul>

                <Footer />

                <ConfirmPopup 
                    onRequestOpen={this.state.openClosePopup}
                    onSave={() => (
                        dispatch(setAppFormSave()),
                        this.setState({openClosePopup: false}))
                    }
                    onConfirm={() => (
                        dispatch(setAppFormCancel()),
                        this.setState({openClosePopup: false}))
                    }
                    onCancel={() => this.setState({openClosePopup: false})}
                />
            </nav>

        )
    }

    render() {
        const {model_runs, sos_models, sector_models, scenarios, isFetching} = this.props
        const pathname = this.props.location.pathname

        if (this.props.app.redirect != '' && this.props.app.redirect != pathname && this.props.app.formEdit == false && this.props.app.formError == false && this.props.app.formSaving == false) {
            return (
                <div>
                    <Redirect to={this.props.app.redirect} />
                </div>
            )
        }
        else if (isFetching && this.init) {
            return this.renderLoading()
        } else {
            this.init = false
            return this.renderNav(model_runs, sos_models, sector_models, scenarios)
        }
    }
}

Nav.propTypes = {
    app: PropTypes.object.isRequired,
    model_runs: PropTypes.array.isRequired,
    sos_models: PropTypes.array.isRequired,
    sector_models: PropTypes.array.isRequired,
    scenarios: PropTypes.array.isRequired,
    isFetching: PropTypes.bool.isRequired,
    dispatch: PropTypes.func.isRequired,
    location: PropTypes.object.isRequired
}

function mapStateToProps(state) {
    const { model_runs, sos_models, sector_models, scenarios } = state
    return {
        app: state.app,
        model_runs: model_runs.items,
        sos_models: sos_models.items,
        sector_models: sector_models.items,
        scenarios: scenarios.items,

        isFetching: (
            state.model_runs.isFetching ||
            state.sos_models.isFetching ||
            state.sector_models.isFetching ||
            state.scenarios.isFetching
        )
    }
}

export default connect(mapStateToProps)(Nav)
