#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dmplexsnes.c */
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
#include "petscsnes.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsnescomputeobjectivefem_ DMPLEXSNESCOMPUTEOBJECTIVEFEM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsnescomputeobjectivefem_ dmplexsnescomputeobjectivefem
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsnescomputeresidualfem_ DMPLEXSNESCOMPUTERESIDUALFEM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsnescomputeresidualfem_ dmplexsnescomputeresidualfem
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsnescomputeresidualds_ DMPLEXSNESCOMPUTERESIDUALDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsnescomputeresidualds_ dmplexsnescomputeresidualds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsnescomputeboundaryfem_ DMPLEXSNESCOMPUTEBOUNDARYFEM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsnescomputeboundaryfem_ dmplexsnescomputeboundaryfem
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsnescomputejacobianaction_ DMSNESCOMPUTEJACOBIANACTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsnescomputejacobianaction_ dmsnescomputejacobianaction
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsnescomputejacobianfem_ DMPLEXSNESCOMPUTEJACOBIANFEM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsnescomputejacobianfem_ dmplexsnescomputejacobianfem
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsnescreatejacobianmf_ DMSNESCREATEJACOBIANMF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsnescreatejacobianmf_ dmsnescreatejacobianmf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetsneslocalfem_ DMPLEXSETSNESLOCALFEM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetsneslocalfem_ dmplexsetsneslocalfem
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsnescheckdiscretization_ DMSNESCHECKDISCRETIZATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsnescheckdiscretization_ dmsnescheckdiscretization
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsnescheckresidual_ DMSNESCHECKRESIDUAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsnescheckresidual_ dmsnescheckresidual
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsnescheckjacobian_ DMSNESCHECKJACOBIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsnescheckjacobian_ dmsnescheckjacobian
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsnescheckfromoptions_ DMSNESCHECKFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsnescheckfromoptions_ dmsnescheckfromoptions
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmplexsnescomputeobjectivefem_(DM dm,Vec X,PetscReal *obj,void*user, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLREAL(obj);
*ierr = DMPlexSNESComputeObjectiveFEM(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((X) ),obj,user);
}
PETSC_EXTERN void  dmplexsnescomputeresidualfem_(DM dm,Vec X,Vec F,void*user, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(F);
*ierr = DMPlexSNESComputeResidualFEM(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((X) ),
	(Vec)PetscToPointer((F) ),user);
}
PETSC_EXTERN void  dmplexsnescomputeresidualds_(DM dm,Vec X,Vec F,void*user, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(F);
*ierr = DMPlexSNESComputeResidualDS(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((X) ),
	(Vec)PetscToPointer((F) ),user);
}
PETSC_EXTERN void  dmplexsnescomputeboundaryfem_(DM dm,Vec X,void*user, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(X);
*ierr = DMPlexSNESComputeBoundaryFEM(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((X) ),user);
}
PETSC_EXTERN void  dmsnescomputejacobianaction_(DM dm,Vec X,Vec Y,Vec F,void*user, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(Y);
CHKFORTRANNULLOBJECT(F);
*ierr = DMSNESComputeJacobianAction(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((X) ),
	(Vec)PetscToPointer((Y) ),
	(Vec)PetscToPointer((F) ),user);
}
PETSC_EXTERN void  dmplexsnescomputejacobianfem_(DM dm,Vec X,Mat Jac,Mat JacP,void*user, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(Jac);
CHKFORTRANNULLOBJECT(JacP);
*ierr = DMPlexSNESComputeJacobianFEM(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((X) ),
	(Mat)PetscToPointer((Jac) ),
	(Mat)PetscToPointer((JacP) ),user);
}
PETSC_EXTERN void  dmsnescreatejacobianmf_(DM dm,Vec X,void*user,Mat *J, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(X);
PetscBool J_null = !*(void**) J ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(J);
*ierr = DMSNESCreateJacobianMF(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((X) ),user,J);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! J_null && !*(void**) J) * (void **) J = (void *)-2;
}
PETSC_EXTERN void  dmplexsetsneslocalfem_(DM dm,PetscBool *use_obj,void*ctx, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexSetSNESLocalFEM(
	(DM)PetscToPointer((dm) ),*use_obj,ctx);
}
PETSC_EXTERN void  dmsnescheckdiscretization_(SNES snes,DM dm,PetscReal *t,Vec u,PetscReal *tol,PetscReal error[], int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(u);
CHKFORTRANNULLREAL(error);
*ierr = DMSNESCheckDiscretization(
	(SNES)PetscToPointer((snes) ),
	(DM)PetscToPointer((dm) ),*t,
	(Vec)PetscToPointer((u) ),*tol,error);
}
PETSC_EXTERN void  dmsnescheckresidual_(SNES snes,DM dm,Vec u,PetscReal *tol,PetscReal *residual, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(u);
CHKFORTRANNULLREAL(residual);
*ierr = DMSNESCheckResidual(
	(SNES)PetscToPointer((snes) ),
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((u) ),*tol,residual);
}
PETSC_EXTERN void  dmsnescheckjacobian_(SNES snes,DM dm,Vec u,PetscReal *tol,PetscBool *isLinear,PetscReal *convRate, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(u);
CHKFORTRANNULLREAL(convRate);
*ierr = DMSNESCheckJacobian(
	(SNES)PetscToPointer((snes) ),
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((u) ),*tol,isLinear,convRate);
}
PETSC_EXTERN void  dmsnescheckfromoptions_(SNES snes,Vec u, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(u);
*ierr = DMSNESCheckFromOptions(
	(SNES)PetscToPointer((snes) ),
	(Vec)PetscToPointer((u) ));
}
#if defined(__cplusplus)
}
#endif
