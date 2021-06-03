import React from 'react';
import { makeStyles } from "@material-ui/styles";
import { Grid, Link as MuiLink, AppBar, Toolbar } from "@material-ui/core";
import {  Link } from "react-router-dom";

const useStyles = makeStyles(theme => ({
    linkText: {
        textDecoration: `none`,
        textTransform: `uppercase`,
        color: `white`
    }
}))

const Header = props => {
    const classes = useStyles();
    return (
        <AppBar position='static'>
            <Toolbar variant='regular'>
                <Grid container alignContent='center' >
                    <Link to='/' className={classes.linkText}>
                        CoWin Notifier
                    </Link>
                </Grid>
                <Grid container alignContent='center' justify='flex-end'>
                    <Link to='/subscriptions' className={classes.linkText} style={{paddingRight: 24}}>
                        Subscription
                    </Link>
                    <Link to='/stream/subscriptions' className={classes.linkText}>
                        Real-time Subscriptions
                    </Link>
                </Grid>
        </Toolbar>
      </AppBar>
    );
}

export default Header;