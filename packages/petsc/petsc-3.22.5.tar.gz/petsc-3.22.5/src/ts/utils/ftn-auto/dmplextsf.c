#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dmplexts.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscdmplex.h"
#include "petscts.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextscomputerhsfunctionfvm_ DMPLEXTSCOMPUTERHSFUNCTIONFVM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextscomputerhsfunctionfvm_ dmplextscomputerhsfunctionfvm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextscomputeboundary_ DMPLEXTSCOMPUTEBOUNDARY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextscomputeboundary_ dmplextscomputeboundary
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextscomputeifunctionfem_ DMPLEXTSCOMPUTEIFUNCTIONFEM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextscomputeifunctionfem_ dmplextscomputeifunctionfem
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextscomputeijacobianfem_ DMPLEXTSCOMPUTEIJACOBIANFEM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextscomputeijacobianfem_ dmplextscomputeijacobianfem
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextscomputerhsfunctionfem_ DMPLEXTSCOMPUTERHSFUNCTIONFEM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextscomputerhsfunctionfem_ dmplextscomputerhsfunctionfem
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmtscheckresidual_ DMTSCHECKRESIDUAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmtscheckresidual_ dmtscheckresidual
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmtscheckjacobian_ DMTSCHECKJACOBIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmtscheckjacobian_ dmtscheckjacobian
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmplextscomputerhsfunctionfvm_(DM dm,PetscReal *time,Vec locX,Vec F,void*user, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(locX);
CHKFORTRANNULLOBJECT(F);
*ierr = DMPlexTSComputeRHSFunctionFVM(
	(DM)PetscToPointer((dm) ),*time,
	(Vec)PetscToPointer((locX) ),
	(Vec)PetscToPointer((F) ),user);
}
PETSC_EXTERN void  dmplextscomputeboundary_(DM dm,PetscReal *time,Vec locX,Vec locX_t,void*user, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(locX);
CHKFORTRANNULLOBJECT(locX_t);
*ierr = DMPlexTSComputeBoundary(
	(DM)PetscToPointer((dm) ),*time,
	(Vec)PetscToPointer((locX) ),
	(Vec)PetscToPointer((locX_t) ),user);
}
PETSC_EXTERN void  dmplextscomputeifunctionfem_(DM dm,PetscReal *time,Vec locX,Vec locX_t,Vec locF,void*user, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(locX);
CHKFORTRANNULLOBJECT(locX_t);
CHKFORTRANNULLOBJECT(locF);
*ierr = DMPlexTSComputeIFunctionFEM(
	(DM)PetscToPointer((dm) ),*time,
	(Vec)PetscToPointer((locX) ),
	(Vec)PetscToPointer((locX_t) ),
	(Vec)PetscToPointer((locF) ),user);
}
PETSC_EXTERN void  dmplextscomputeijacobianfem_(DM dm,PetscReal *time,Vec locX,Vec locX_t,PetscReal *X_tShift,Mat Jac,Mat JacP,void*user, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(locX);
CHKFORTRANNULLOBJECT(locX_t);
CHKFORTRANNULLOBJECT(Jac);
CHKFORTRANNULLOBJECT(JacP);
*ierr = DMPlexTSComputeIJacobianFEM(
	(DM)PetscToPointer((dm) ),*time,
	(Vec)PetscToPointer((locX) ),
	(Vec)PetscToPointer((locX_t) ),*X_tShift,
	(Mat)PetscToPointer((Jac) ),
	(Mat)PetscToPointer((JacP) ),user);
}
PETSC_EXTERN void  dmplextscomputerhsfunctionfem_(DM dm,PetscReal *time,Vec locX,Vec locG,void*user, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(locX);
CHKFORTRANNULLOBJECT(locG);
*ierr = DMPlexTSComputeRHSFunctionFEM(
	(DM)PetscToPointer((dm) ),*time,
	(Vec)PetscToPointer((locX) ),
	(Vec)PetscToPointer((locG) ),user);
}
PETSC_EXTERN void  dmtscheckresidual_(TS ts,DM dm,PetscReal *t,Vec u,Vec u_t,PetscReal *tol,PetscReal *residual, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(u);
CHKFORTRANNULLOBJECT(u_t);
CHKFORTRANNULLREAL(residual);
*ierr = DMTSCheckResidual(
	(TS)PetscToPointer((ts) ),
	(DM)PetscToPointer((dm) ),*t,
	(Vec)PetscToPointer((u) ),
	(Vec)PetscToPointer((u_t) ),*tol,residual);
}
PETSC_EXTERN void  dmtscheckjacobian_(TS ts,DM dm,PetscReal *t,Vec u,Vec u_t,PetscReal *tol,PetscBool *isLinear,PetscReal *convRate, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(u);
CHKFORTRANNULLOBJECT(u_t);
CHKFORTRANNULLREAL(convRate);
*ierr = DMTSCheckJacobian(
	(TS)PetscToPointer((ts) ),
	(DM)PetscToPointer((dm) ),*t,
	(Vec)PetscToPointer((u) ),
	(Vec)PetscToPointer((u_t) ),*tol,isLinear,convRate);
}
#if defined(__cplusplus)
}
#endif
